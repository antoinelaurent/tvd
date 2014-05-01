from tvd import AnnotationGraph, Episode, TAnchored, TFloating, TStart, TEnd
import re
import networkx as nx

class CTMAligner(object):
	"""docstring for CTMParser"""
	def __init__(self, punctuation=True):
		super(CTMAligner, self).__init__()
		self.punctuation = punctuation

	def clean_sentence(self, sentenceWords):
		sentenceClean = re.sub(r'\([^\)]+\)','', sentenceWords)
		sentenceClean = re.sub(r'\[[^\]]+\]','', sentenceClean)
		#sentenceClean = re.sub('[.!,;?":]','', sentenceClean)
			
		sentenceClean = re.sub(r'^[\.!,;?":]+','', sentenceClean)

		sentenceClean = re.sub(r'([\.!,;?":]+)[ ]+([\.!,;?":]+)','\g<1>\g<2>', sentenceClean)
		sentenceClean = re.sub(r'[ ]*([\.!,;?":]+)','\g<1> ', sentenceClean)

		sentenceClean = re.sub(r' +',' ', sentenceClean)
		sentenceClean = sentenceClean.strip()
		return sentenceClean
	
	def merge_ctm_with_manual_transcript(self, ctmGraph, manualTranscriptGraph):
		lastIndexNode=0

		end = False
		
		TFloating.reset()
		manualTranscriptGraph, map = manualTranscriptGraph.relabel_floating_nodes()
		ctmGraph, map2 = ctmGraph.relabel_floating_nodes()

		manualTranscriptGraph, map = manualTranscriptGraph.relabel_floating_nodes(mapping=map)

		nodesWords = nx.topological_sort(ctmGraph)
		if nodesWords[lastIndexNode] == TStart():
			lastIndexNode += 1

		last = -1
		next = -1

		first_node = None

		first = -1
		for t1, t2, data in manualTranscriptGraph.ordered_edges_iter(data=True):
			if 'speech' in data:
				sentence = data['speech']
				speaker = data['speaker']
				sentenceClean = self.clean_sentence(sentence)
				if not self.punctuation:
					sentenceClean = re.sub(r'[\.!,;?":]+','', sentenceClean)

				if sentenceClean != "":

					sentenceWords = ""
				
					if lastIndexNode < len(nodesWords):

						if first_node is None and t1 != TStart():
							first_node = t1
							manualTranscriptGraph.add_annotation(first_node, nodesWords[lastIndexNode])

						node_manual_trs_start = t1
						node_manual_trs_end = t2

						node_float = TFloating()
						remainingData = None
						if last > 0 and next > 0:
							for key in ctmGraph[last][next]:
								dataWord = ctmGraph[last][next][key]
								if 'speech' in dataWord:
									remainingData = dataWord
									sentenceWords = remainingData['speech']
									sentenceWords = self.clean_sentence(sentenceWords)
									last = -1
									next = -1
						
						bAlreadyAdded = False

						if(remainingData is not None):
							if 'speech' in remainingData:
								remainingData['speaker']=speaker
							manualTranscriptGraph.add_annotation(node_manual_trs_start, nodesWords[lastIndexNode], data=remainingData)
							if sentenceWords == sentenceClean:
								manualTranscriptGraph.add_annotation(nodesWords[lastIndexNode], node_manual_trs_end)
								bAlreadyAdded = True

						if not bAlreadyAdded:
							if not manualTranscriptGraph.has_edge(node_manual_trs_start, nodesWords[lastIndexNode]):
								manualTranscriptGraph.add_annotation(node_manual_trs_start, nodesWords[lastIndexNode])

							node_end = ""
							previousNode = None
							while not end and lastIndexNode < len(nodesWords):
								node = nodesWords[lastIndexNode]
								for node2 in sorted(ctmGraph.successors(node)):
									
									node_start = node
									node_end = node2
									
									if previousNode is not None:
										if not manualTranscriptGraph.has_edge(previousNode, node_start) and previousNode != node_start :
											manualTranscriptGraph.add_annotation(previousNode, node_start)

									for key in ctmGraph[node][node2]:
										dataWord = ctmGraph[node][node2][key]
										if 'speech' in dataWord:
											dataWord['speaker']=speaker
										manualTranscriptGraph.add_annotation(node_start, node_end, data=dataWord)
									
										if 'speech' in dataWord:
											if sentenceWords == "":
												sentenceWords = dataWord['speech']
											else:
												sentenceWords += " " + dataWord['speech']
											sentenceWords = self.clean_sentence(sentenceWords)
									if sentenceWords == sentenceClean:
										if re.search(r'[\.!,;?":]$', sentenceClean):
											#Have to add the next anchored just before the end of the speech turn ...
											lastIndexNode+= 2
											if lastIndexNode < len(nodesWords):
												node = nodesWords[lastIndexNode]
												if node.is_anchored:
													manualTranscriptGraph.add_annotation(node_end, node)
													node_end = node
													lastIndexNode -= 1
												else:
													lastIndexNode -= 2
										end = True
									previousNode = node_end
								lastIndexNode+=1

							if lastIndexNode+1 < len(nodesWords):
								last = nodesWords[lastIndexNode]
								next = nodesWords[lastIndexNode+1]

							#print "%s -> %s" % (node_end, node_manual_trs_end)
							lastIndexNode+=1

							manualTranscriptGraph.add_annotation(node_end, node_manual_trs_end)
							
							end = False
					elif sentenceClean != "":
						print "Unable to align '%s' !" % (sentenceClean)
						return None

		return manualTranscriptGraph
