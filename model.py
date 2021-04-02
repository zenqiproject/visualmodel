import matplotlib
import os, sys
import yaml
from argparse import ArgumentParser
from tqdm import tqdm

import imageio
import numpy as np
from skimage.transform import resize
from skimage import img_as_ubyte
import torch
from sync_batchnorm import DataParallelWithCallback
import threading

from modules.generator import OcclusionAwareGenerator
from modules.keypoint_detector import KPDetector
from animate import normalize_kp
from scipy.spatial import ConvexHull

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QFileDialog, \
	QProgressBar, QDialog, QPushButton
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread, QObject
from PyQt5 import QtCore
from UI import MaterialButton, Button, MaterialCard, LineEdit, SeleniumUIButton, ToggleSwitch
import resources
import os
import save
import json
import subprocess
from datetime import datetime
from utils import readWindowSettings

matplotlib.use('Agg')

class TranslucentWidgetSignals(QObject):
    # SIGNALS
    CLOSE = pyqtSignal()

class TranslucentWidget(QWidget):
    def __init__(self, parent=None):
        super(TranslucentWidget, self).__init__(parent)

        # make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.fillColor = QColor(20, 20, 20, 120)
        self.penColor = QColor("#333333")

        self.popup_fillColor = QColor(38, 38, 38)
        self.popup_penColor = QColor(38, 38, 38)

        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(QIcon(":icon/close.png"))

        self.cancel = QPushButton("CANCEL", self)
        self.updatebtn = QPushButton("OK", self)

        self.cancel.setFixedSize(70, 20)
        self.updatebtn.setFixedSize(70,20)

        self.setStyleSheet("""
		QPushButton{
			border-radius: 10px;
			background-color: transparent;
			border: 1px solid rgb(224, 224, 224);
			font-size: 7pt;
			letter-spacing: 10pt;
		}
		QPushButton:hover{
			background-color: rgb(118, 118, 118);
			border: none;
		}
		QPushButton:pressed{
			background-color: rgb(106, 106, 106);
			border: none;
		}
		""")

        self.updatelbl = QLabel(f"Finished exporing video.", self)
        self.updatelbl.setFont(QFont("Muli"))
        self.close_btn.setStyleSheet("background-color: transparent;\nborder: none;")

        self.close_btn.setFixedSize(30, 30)
        self.cancel.clicked.connect(self._onclose)
        self.close_btn.clicked.connect(self._onclose)

        self.SIGNALS = TranslucentWidgetSignals()

    def resizeEvent(self, event):
        s = self.size()
        popup_width = 300
        popup_height = 120
        ow = int(s.width() / 2 - popup_width / 2)
        oh = int(s.height() / 2 - popup_height / 2)

        self.cancel.move(ow + 120, oh + 85)
        self.updatebtn.move(ow + 200, oh + 85)
        self.updatelbl.move(ow + 20, oh + 20)

        self.close_btn.move(ow + 265, oh + 5)
        tolw, tolh = 80, -5


    def paintEvent(self, event):
        # This method is, in practice, drawing the contents of
        # your window.

        # get current window size
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(self.penColor)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        # drawpopup
        qp.setPen(self.popup_penColor)
        qp.setBrush(self.popup_fillColor)
        popup_width = 300
        popup_height = 120
        ow = int(s.width()/2-popup_width/2)
        oh = int(s.height()/2-popup_height/2)
        qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)

        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        qp.setFont(font)
        qp.setPen(QColor(70, 70, 70))


        qp.end()

    def _onclose(self):
        print("Close")
        self.SIGNALS.CLOSE.emit()


class Thread(QThread):
	_signal = pyqtSignal(int)

	def __init__(self, checkpoint, config, source_image, source_video, iscpu=False, output=""):
		super(Thread, self).__init__()
		self.checkpoint = checkpoint
		self.config = config
		self.source_image = source_image
		self.source_video = source_video
		self.cpu = iscpu
		self.result_video = output
		self.threadrunning = True

	def run(self):

		if sys.version_info[0] < 3:
			raise Exception("You must use Python 3 or higher. Recommended version is Python 3.7")

		def load_checkpoints(config_path, checkpoint_path, cpu=False):

			with open(config_path) as f:
				config = yaml.load(f)

			generator = OcclusionAwareGenerator(**config['model_params']['generator_params'],
												**config['model_params']['common_params'])
			if not cpu:
				generator.cuda()

			kp_detector = KPDetector(**config['model_params']['kp_detector_params'],
									 **config['model_params']['common_params'])
			if not cpu:
				kp_detector.cuda()

			if cpu:
				checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
			else:
				checkpoint = torch.load(checkpoint_path)

			generator.load_state_dict(checkpoint['generator'])
			kp_detector.load_state_dict(checkpoint['kp_detector'])

			if not cpu:
				generator = DataParallelWithCallback(generator)
				kp_detector = DataParallelWithCallback(kp_detector)

			generator.eval()
			kp_detector.eval()

			return generator, kp_detector

		def make_animation(source_image, driving_video, generator, kp_detector, relative=True,
						   adapt_movement_scale=True, cpu=False):
			with torch.no_grad():
				predictions = []
				source = torch.tensor(source_image[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2)
				if not cpu:
					source = source.cuda()
				driving = torch.tensor(np.array(driving_video)[np.newaxis].astype(np.float32)).permute(0, 4, 1, 2, 3)
				kp_source = kp_detector(source)
				kp_driving_initial = kp_detector(driving[:, :, 0])

				for frame_idx in tqdm(range(driving.shape[2])):
					self._signal.emit(frame_idx / driving.shape[2] * 100)
					driving_frame = driving[:, :, frame_idx]
					if not cpu:
						driving_frame = driving_frame.cuda()
					kp_driving = kp_detector(driving_frame)
					kp_norm = normalize_kp(kp_source=kp_source, kp_driving=kp_driving,
										   kp_driving_initial=kp_driving_initial, use_relative_movement=relative,
										   use_relative_jacobian=relative, adapt_movement_scale=adapt_movement_scale)
					out = generator(source, kp_source=kp_source, kp_driving=kp_norm)

					predictions.append(np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0])
			return predictions

		def find_best_frame(source, driving, cpu=False):
			import face_alignment

			def normalize_kp(kp):
				kp = kp - kp.mean(axis=0, keepdims=True)
				area = ConvexHull(kp[:, :2]).volume
				area = np.sqrt(area)
				kp[:, :2] = kp[:, :2] / area
				return kp

			fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=True,
											  device='cpu' if cpu else 'cuda')
			kp_source = fa.get_landmarks(255 * source)[0]
			kp_source = normalize_kp(kp_source)
			norm = float('inf')
			frame_num = 0
			for i, image in tqdm(enumerate(driving)):
				kp_driving = fa.get_landmarks(255 * image)[0]
				kp_driving = normalize_kp(kp_driving)
				new_norm = (np.abs(kp_source - kp_driving) ** 2).sum()
				if new_norm < norm:
					norm = new_norm
					frame_num = i
			return frame_num

		source_image = imageio.imread(self.source_image)
		reader = imageio.get_reader(self.source_video)
		fps = reader.get_meta_data()['fps']
		driving_video = []
		try:
			for im in reader:
				driving_video.append(im)
		except RuntimeError:
			pass
		reader.close()
		#print(driving_video)
		source_image = resize(source_image, (256, 256))[..., :3]
		driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
		generator, kp_detector = load_checkpoints(config_path=self.config, checkpoint_path=self.checkpoint, cpu=self.cpu)

		predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=True,
									 adapt_movement_scale=True, cpu=self.cpu)
		imageio.mimsave(self.result_video, [img_as_ubyte(frame) for frame in predictions], fps=fps)

	def stop(self):
		self.threadrunning = False
		self.wait()

class SlidingStackedWidget(QStackedWidget):
	def __init__(self, parent=None):
		super(SlidingStackedWidget, self).__init__(parent)
		self.m_direction = QtCore.Qt.Horizontal
		self.m_speed = 500
		self.m_animationtype = QtCore.QEasingCurve.OutCubic
		self.m_now = 0
		self.m_next = 0
		self.m_wrap = False
		self.m_pnow = QtCore.QPoint(0, 0)
		self.m_active = False

	def setDirection(self, direction):
		self.m_direction = direction

	def setSpeed(self, speed):
		self.m_speed = speed

	def setAnimation(self, animationtype):
		self.m_animationtype = animationtype

	def setWrap(self, wrap):
		self.m_wrap = wrap

	@QtCore.pyqtSlot()
	def slideInPrev(self):
		now = self.currentIndex()
		if self.m_wrap or now > 0:
			self.slideInIdx(now - 1)

	@QtCore.pyqtSlot()
	def slideInNext(self):
		now = self.currentIndex()
		if self.m_wrap or now < (self.count() - 1):
			self.slideInIdx(now + 1)

	def slideInIdx(self, idx):
		if idx > (self.count() - 1):
			idx = idx % self.count()
		elif idx < 0:
			idx = (idx + self.count()) % self.count()
		self.slideInWgt(self.widget(idx))

	def slideInWgt(self, newwidget):
		if self.m_active:
			return

		self.m_active = True

		_now = self.currentIndex()
		_next = self.indexOf(newwidget)

		if _now == _next:
			self.m_active = False
			return

		offsetx, offsety = self.frameRect().width(), self.frameRect().height()
		self.widget(_next).setGeometry(self.frameRect())

		if not self.m_direction == QtCore.Qt.Horizontal:
			if _now < _next:
				offsetx, offsety = 0, -offsety
			else:
				offsetx = 0
		else:
			if _now < _next:
				offsetx, offsety = -offsetx, 0
			else:
				offsety = 0

		pnext = self.widget(_next).pos()
		pnow = self.widget(_now).pos()
		self.m_pnow = pnow

		offset = QtCore.QPoint(offsetx, offsety)
		self.widget(_next).move(pnext - offset)
		self.widget(_next).show()
		self.widget(_next).raise_()

		anim_group = QtCore.QParallelAnimationGroup(
			self, finished=self.animationDoneSlot
		)

		for index, start, end in zip(
			(_now, _next), (pnow, pnext - offset), (pnow + offset, pnext)
		):
			animation = QtCore.QPropertyAnimation(
				self.widget(index),
				b"pos",
				duration=self.m_speed,
				easingCurve=self.m_animationtype,
				startValue=start,
				endValue=end,
			)
			anim_group.addAnimation(animation)

		self.m_next = _next
		self.m_now = _now
		self.m_active = True
		anim_group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

	@QtCore.pyqtSlot()
	def animationDoneSlot(self):
		self.setCurrentIndex(self.m_next)
		self.widget(self.m_now).hide()
		self.widget(self.m_now).move(self.m_pnow)
		self.m_active = False


class VideoView(MaterialCard):
	video_path = None
	def __init__(self):
		super(VideoView, self).__init__()

		self.lbl = QLabel(" ".join("select a video"))
		self.lbl.setFont(QFont("Muli"))



		self.vbox = QVBoxLayout()
		self.vbox.addWidget(self.lbl, alignment=Qt.AlignCenter)
		self.setLayout(self.vbox)

	def mousePressEvent(self, event):
		print("Choose picture")
		filename, _ = QFileDialog.getOpenFileName(self, "Select a video", os.getcwd(), "Video Files (*.mp4 *.avi);;All Files (*)")
		if filename != "":
			self.addVideo(filename)


	def addVideo(self, filename):
		import random
		self.video_path = filename
		bin = os.getcwd() + "\\ffmpeg.exe"
		tmpfolder = os.getcwd() + "\\tmp"

		if os.path.isdir(tmpfolder) != True:
			os.mkdir(tmpfolder)


		randomnum = "".join(str(random.randint(0,9)) for _ in range(10))

		subprocess.call(['ffmpeg', '-i', filename, '-ss', '00:00:00.000', '-vframes', '1', f"{tmpfolder}\\{randomnum}.png"])
		print(randomnum)
		pixmap = QPixmap(os.getcwd() + f"\\tmp\\{randomnum}.png")
		self.lbl.setPixmap(pixmap.scaled(QSize(150, 150), Qt.KeepAspectRatio, Qt.SmoothTransformation))

class ImageView(MaterialCard):
	image_filename = None
	def __init__(self):
		super(ImageView, self).__init__()
		self.background = "rgb(20, 20, 20)"

		self.img = QLabel(" ".join("select an image"))
		self.img.setFont(QFont("Muli"))
		vbox = QVBoxLayout()

		vbox.addWidget(self.img, alignment=Qt.AlignCenter)
		self.setLayout(vbox)



	def mousePressEvent(self, event):
		print("Choose picture")
		filename, _ = QFileDialog.getOpenFileName(self, "Select an image", os.getcwd(), "Image Files (*.png *.jpg *.bmp);;All Files (*)")
		self.changeImage(filename)

	def changeImage(self, filename):
		self.image_filename = filename
		pixmap = QPixmap(filename)
		self.img.setPixmap(pixmap.scaled(QSize(150, 150), Qt.KeepAspectRatio, Qt.SmoothTransformation))

class MyModel(QWidget):
	is_my_model_active = False
	def __init__(self):
		super(MyModel, self).__init__()
		if self.is_my_model_active:
			nosavelbl = QLabel("no saved models")
			nosavelbl.setFont(QFont("Muli"))
			nosavelbl.setAlignment(Qt.AlignCenter)



class ModelView(QWidget):
	def __init__(self, parent=None):
		super(ModelView, self).__init__(parent=None)



		hbuttonlayout = QHBoxLayout()
		self.savebtn = SeleniumUIButton("SAVE", width=90, height=20)
		self.savebtn.clicked.connect(self.saveFile)


		self.exportbtn = SeleniumUIButton("NEXT", width=90, height=20)


		hcardlayout = QHBoxLayout()
		self.imagecard = ImageView()

		self.videocard = VideoView()

		hcardlayout.addWidget(self.imagecard)
		hcardlayout.addWidget(self.videocard)
		hcardlayout.setAlignment(Qt.AlignCenter)

		hbuttonlayout.addWidget(self.savebtn)
		hbuttonlayout.addWidget(self.exportbtn)
		hbuttonlayout.setAlignment(Qt.AlignCenter)

		vbox = QVBoxLayout()

		vbox.addLayout(hcardlayout)
		vbox.addLayout(hbuttonlayout)
		self.setLayout(vbox)


	def get_file_paths(self):
		imagepath = self.imagecard.image_filename
		videopath = self.videocard.video_path

		return imagepath, videopath

	def saveFile(self):
		file, _ = QFileDialog.getSaveFileName(self, "Save File", os.getcwd(), "Visual Model Project (*.vmp)")

		saved_data = {}
		saved_data["imagePath"] = self.imagecard.image_filename
		saved_data["videoPath"] = self.videocard.video_path

		if file != "":
			save.save_file(file, saved_data)

		print(file)



class ExportView(QWidget):

	is_back_pressed = pyqtSignal()
	def __init__(self, parent=None):
		super(ExportView, self).__init__(parent=None)


		hbuttonlayout = QHBoxLayout()
		self.savebtn = SeleniumUIButton("SAVE", width=90, height=20)


		self.exportbtn = SeleniumUIButton("EXPORT", width=90, height=20)
		self.exportbtn.clicked.connect(self.exporting)

		vcardlayout = QVBoxLayout()

		self.iscpu = False

		iscpulayout = QHBoxLayout()

		self.cpuSwitch = ToggleSwitch(isOn=False)
		self.cpuSwitch.clicked.connect(self.settings)

		cpulabel = QLabel("allow cuda for acceleration\n(Dont allow if you havent installed cuda)")
		cpulabel.setFont(QFont("Muli"))

		iscpulayout.setAlignment(Qt.AlignTop)
		iscpulayout.addWidget(cpulabel)
		iscpulayout.addWidget(self.cpuSwitch)

		vcardlayout.addLayout(iscpulayout)

		card = MaterialCard()
		card.setFixedWidth(350)
		card.setLayout(vcardlayout)

		hbuttonlayout.addWidget(self.savebtn)
		hbuttonlayout.addWidget(self.exportbtn)
		hbuttonlayout.setAlignment(Qt.AlignCenter)

		self.backbtn = SeleniumUIButton("", width=32, height=32, icon=":/icon/back.png")
		self.backbtn.setStyleSheet("""
		QPushButton{
			border-radius: 10px;
			background-color: transparent;
			border: transparent;
			font-size: 7pt;
			letter-spacing: 10pt;
		}
		QPushButton:hover{
			background-color: rgb(118, 118, 118);
			border: none;
		}
		QPushButton:pressed{
			background-color: rgb(106, 106, 106);
			border: none;
		}
		""")
		self.backbtn.clicked.connect(lambda: self.is_back_pressed.emit())

		self.vbox = QVBoxLayout()

		self.pbar = QProgressBar()
		self.pbar.setStyleSheet("""
		QProgressBar{
			background: transparent;
			border: 1px solid rgb(118, 118, 118);
		}
		QProgressBar::chunk {
		    background-color: #767676;
		}
		""")
		self.pbar.setFixedSize(300, 10)
		self.pbar.hide()

		self.vbox.addWidget(self.backbtn, alignment=Qt.AlignLeft)
		self.vbox.addWidget(card, alignment=Qt.AlignCenter)
		self.vbox.addWidget(self.pbar, alignment=Qt.AlignCenter)
		self.vbox.addLayout(hbuttonlayout)
		self.setLayout(self.vbox)

	def settings(self):
		if self.cpuSwitch.isChecked():
			print("True")
			self.iscpu = True
		else:
			print("False")
			self.iscpu = False

	def signal_accept(self, percentage):


		self.pbar.setValue(percentage)
		self.pbar.setTextVisible(False)
		if self.pbar.value() == 99:
			self.pbar.setValue(100)
			print("done")

	def exporting(self):
		print()
		self.pbar.show()
		self.exportbtn.setEnabled(False)
		with open(os.getcwd() + "\\tmp\\export.json", "r") as f:
			data = json.load(f)

		checkpoint = f"{readWindowSettings('dataset_path')}\\vox-adv-cpk.pth.tar"
		config = os.getcwd() + "\\config\\vox-256.yaml"

		print(data["imagepath"], data["videopath"])
		output_path = f'{readWindowSettings("output_path")}\\{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.mp4'
		print(output_path)
		self.thread = Thread(checkpoint=checkpoint, config=config,
							 source_image=data["imagepath"], source_video=data["videopath"],
							 iscpu=False, output=output_path)

		self.thread._signal.connect(self.signal_accept)
		self.thread.start()

		#print(data["imagepath"], data["videopath"])

class ModelBase(SlidingStackedWidget):
	def __init__(self):
		super(ModelBase, self).__init__()

		self.modelviewbase = ModelView()
		self.exportviewbase = ExportView()
		self.exportviewbase.is_back_pressed.connect(self.changeModelView)


		self.addWidget(self.modelviewbase)
		self.addWidget(self.exportviewbase)

		self.setCurrentIndex(0)
		self.modelviewbase.exportbtn.clicked.connect(self.changeExportView)

	def changeExportView(self):
		print("Exporting project")



		tmpfolder = os.getcwd() + "\\tmp"
		imagepath, videopath = self.modelviewbase.get_file_paths()

		print(imagepath, videopath)
		if imagepath != None and videopath != None:
			if os.path.isdir(tmpfolder) != True:
				os.mkdir(tmpfolder)

			with open(tmpfolder + "\\export.json", "w") as f:
				f.write('{ "imagepath": "%s", "videopath": "%s" }' % (imagepath, videopath))
			self.slideInNext()

	def changeModelView(self):
		self.slideInPrev()

