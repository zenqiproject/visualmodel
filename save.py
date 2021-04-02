
import pickle

def save_file(filename, data):
	with open(filename, "wb") as f:
		pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def open_file(filename):
	with open(filename, "rb") as f:
		return pickle.load(f)