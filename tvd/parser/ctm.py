
from tvd import AnnotationGraph, Episode, TAnchored, TFloating, TStart, TEnd
import codecs
import re

class CTMParser(object):
	"""docstring for CTMParser"""
	def __init__(self, punctuation=True):
		super(CTMParser, self).__init__()
		self.punctuation = punctuation

	def get_graph(self, path2ctm):
		g = AnnotationGraph()

		TFloating.reset()
		previousNode = TStart()


		arc = []

		with codecs.open(path2ctm, "rt", encoding='utf8') as f:
			for line in f:
				if not re.search(r'^;;', line):
					fields = line.strip().split()
					start = round(float(fields[2]), 3)
					duration = round(float(fields[3]), 3)
					end = float(start)+float(duration)

					end = round(end, 3)
					
					word = fields[4]

					if not self.punctuation:
						word = re.sub(r'[\.!,;?":]+',' ', word)
						word = re.sub(r' +',' ', word)

					if word != "" and word != ' ':
						confidence = fields[5]
						if duration == 0:
							node_start = previousNode
							node_end = TFloating()
							if len(arc) == 2:
								g.remove_edge(arc[0], arc[1])
								g.add_annotation(arc[0], node_end, arc_data)
								node_inter = TFloating()
								g.add_annotation(node_end, node_inter, data={'speech':word, 'confidence':confidence})
								g.add_annotation(node_inter, arc[1])
								arc.append(node_end)
								arc.append(node_inter)
								node_end=arc[1]
							elif len(arc) > 2:
								node_anc_start = arc[0]
								node_anc_end = arc[1]
								g.remove_edge(arc[len(arc)-1], node_anc_end)
								g.add_annotation(arc[len(arc)-1], node_end, data={'speech':word, 'confidence':confidence})
								g.add_annotation(node_end, node_anc_end)
								arc.append(node_end)
								node_end=arc[1]
						else:
							addEdge = True
							node_start = TAnchored(start)
							node_end = TAnchored(end)
							if previousNode.is_floating:
								if not g.has_edge(previousNode, node_start):
									g.add_annotation(previousNode, node_start)
							else:
								if node_start.T < previousNode.T:
									node_start = previousNode
								elif node_start.T > previousNode.T:
									g.add_annotation(previousNode, node_start)
							if node_start.is_anchored and node_end.is_anchored:
								if node_start.T == node_end.T:
									addEdge = False
									node_start = previousNode
									node_end = TFloating()
									if len(arc) == 2:
										g.remove_edge(arc[0], arc[1])
										g.add_annotation(arc[0], node_end, arc_data)
										node_inter = TFloating()
										g.add_annotation(node_end, node_inter, data={'speech':word, 'confidence':confidence})
										g.add_annotation(node_inter, arc[1])
										arc.append(node_end)
										arc.append(node_inter)
										node_end=arc[1]
									elif len(arc) > 2:
										node_anc_start = arc[0]
										node_anc_end = arc[1]
										g.remove_edge(arc[len(arc)-1], node_anc_end)
										g.add_annotation(arc[len(arc)-1], node_end, data={'speech':word, 'confidence':confidence})
										g.add_annotation(node_end, node_anc_end)
										arc.append(node_end)
										node_end=arc[1]
								else:
									arc = [node_start, node_end]
									arc_data = {'speech':word, 'confidence':confidence}
							if addEdge:
								g.add_annotation(node_start, node_end, data={'speech':word, 'confidence':confidence})
						previousNode=node_end

		g.add_annotation(previousNode, TEnd())
		return g
