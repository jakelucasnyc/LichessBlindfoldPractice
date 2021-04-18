from api.apiGetEvents import APIGetEvents
from api.apiGetGameEvents import APIGetGameEvents
from api.apiPlay import APIPlay
import asyncio
import aiohttp
import logging
from cli import CLI
from cmdHandler import CmdHandler
import threading
from queue import Queue
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def main():

	#initializing objects
	inputQ = Queue()
	globalObjs = {
		# 'APIPlay': APIPlay()
	}
	# outputQ = Queue()
	# apiGetStream = APIGetStream(inputQ)
	# events = asyncio.create_task(apiGetStream.handleEvents())#listening for events
	eventGetter = APIGetEvents(inputQ)
	eventGetter.start()

	time.sleep(1)
	cli = CLI(inputQ)
	cli.start()

	while True:
		
		#example return = ['UserCmd', cmdCls, cmdParams, globalObjList] or ['BackendCmd', 'cmdName', cmdParams, globalObjList] or ['globalObj', 'clsName', 'methodName', paramList]
		#example return = {'type': 'UserCmd', 'cmdCls': 'cmdCls', 'cmdParams': cmdParams, 'objs': globalObjList}
						# {'type': 'BackendCmd', 'cmdName': 'name', 'cmdParams': cmdParams, 'objs': globalObjList}
		qEntry = inputQ.get()
		# print('qEntry', qEntry)
		#send the qEntry to the command handler
		if qEntry['type'] == 'BackendCmd':

			if 'objs' in qEntry.keys():
				objsSent = {clsName: inst for clsName, inst in globalObjs.items() if clsName in qEntry['objs']}
			else:
				objsSent = {}

			cmdResult = CmdHandler.fromBackend(cmdName=qEntry['cmdName'], cmdParams=qEntry['cmdParams'], objDict=objsSent).run()

		elif qEntry['type'] == 'UserCmd':

			if 'objs' in qEntry.keys():
				objsSent = {clsName: inst for clsName, inst in globalObjs.items() if clsName in qEntry['objs']}
			else:
				objsSent = {}

			cmdResult = CmdHandler.fromUser(cmdCls=qEntry['cmdCls'], cmdParams=qEntry['cmdParams'], objDict=objsSent).run()


		# elif qEntry[0] == 'globalObj':
		# 	if qEntry[1] in globalObjs.keys():
		# 		pass
		# 	else:
		# 		pass


		#example cmdResult = [('CRUD', 'obj', 'key', 'value'), ('CRUD', 'obj', 'key', 'value')]
		if not cmdResult:
			continue

		#figure out what to do with the return values of the command
		elif cmdResult[0] == 'APIPlay':
			pass



	# await asyncio.gather(events)







if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main())

	finally:
		loop.run_until_complete(loop.shutdown_asyncgens())
		loop.close()