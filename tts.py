import pyaudio
import json
from watson_developer_cloud import TextToSpeechV1

##THIS CLASS ALSO TAKES CARE OF LEONARDO MOVEMENT
class TTS:

	def __init__(self,stream,cred_file='credentials/ibm_watson.json'):
		with open(cred_file,'r') as file:
			credentials = json.loads(file.read())
			self.client = TextToSpeechV1(
	    		username=credentials['username'],
	    		password=credentials['password'],
	    		x_watson_learning_opt_out=True
	    		)
		self.stream = stream

	##audio rate and chunk size must fit that of stream
	def talk(self,message,accept='audio/l16;rate=16000',chunk_size=1024):
		self.stream.start_stream()
		print("text: " + message)
		audio = self.client.synthesize(
			message,
			accept=accept,
			voice='en-US_MichaelVoice'
			)
		#print(audio.__dict__.keys())
		for i in range(0, len(audio), chunk_size):
			self.stream.write(audio[i:i+chunk_size],exception_on_underflow=False)
		self.stream.stop_stream()



