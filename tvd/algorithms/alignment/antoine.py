from tvd import AnnotationGraph, Episode, TAnchored, TFloating, TStart, TEnd
import codecs
import re
import os
import os.path
import tempfile

def makeCtm(g, wav, output_ctm, path_to_just_vrbs):
	tab = {}
	fic = tempfile.NamedTemporaryFile().name
	namesave = fic.replace("/", "_")

	with codecs.open(fic, 'w', encoding='utf8') as f:
		for t1, t2, data in g.ordered_edges_iter(data=True):
			if 'speech' in data:
				cle = "%s-%s" % (t1.T,t2.T)
				tab[cle]=[]
				f.write("%s-%s#%s#%s\n" % (t1.T,t2.T,data['speaker'],data['speech']))
	cmd = "%s/just_vrbs.pl %s %s %s > %s" % (path_to_just_vrbs, fic, wav, namesave, output_ctm)
	os.system(cmd)

def makeWordGraphFromCtm(ctm, keep_punctuation=False):
	g = AnnotationGraph()
	TFloating.reset()
	previousNode = TFloating()

	with codecs.open(ctm, "rt", encoding='utf8') as f:
		for line in f:
			fields = line.strip().split()
			start = round(float(fields[2]), 3)
			duration = round(float(fields[3]), 3)
			end = float(start)+float(duration)

			end = round(end, 3)
			#end = "%.3f" % round(end,3)
			word = fields[4]

			if not keep_punctuation:
				word = re.sub('[.!,;?"]', '', word)

			if word != "":
				confidence = fields[5]
				if duration == 0:
					node_start = previousNode
					node_end = TFloating()
					g.add_annotation(node_start, node_end, data={'speech':word, 'confidence':confidence})
				else:
					node_start = TAnchored(start)
					node_end = TAnchored(end)
					if previousNode.is_floating:
						g.add_annotation(previousNode, node_start)
					else:
						if node_start.T < previousNode.T:
							node_start = previousNode
						elif node_start.T > previousNode.T:
							g.add_annotation(previousNode, node_start)
					g.add_annotation(node_start, node_end, data={'speech':word, 'confidence':confidence})
				previousNode=node_end
	return g


def mergeGraphs(transcriptGraph, wordsGraph):

	for t1, t2, data in transcriptGraph.ordered_edges_iter(data=True):
		if 'speech' in data:
			sentence = data['speech']
			speaker = data['speaker']
			print sentence
			sentenceClean = re.sub(r'\([^\)]+\)','', sentence)
			sentenceClean = re.sub(r'\[[^\]]+\]','', sentenceClean)
			sentenceClean = re.sub(r' +',' ', sentenceClean)
			sentenceClean = re.sub('[.!,;?"]','', sentenceClean)
			print sentenceClean



def alignTranscript(g, wav, namesave):
	tab = {}

	# with codecs.open('/tmp/dump.txt', 'w', encoding='utf8') as f:
	#     for t1, t2, data in g.ordered_edges_iter(data=True):
	#         if 'speech' in data:
	#               f.write("%s\n" % (data['speech']))

	fic = "/tmp/%s_eti.txt" % namesave

	with codecs.open(fic, 'w', encoding='utf8') as f:
		for t1, t2, data in g.ordered_edges_iter(data=True):
			if 'speech' in data:
				cle = "%s-%s" % (t1.T,t2.T)
				tab[cle]=[]
				f.write("%s-%s#%s#%s\n" % (t1.T,t2.T,data['speaker'],data['speech']))

	out = "dump_clean_%s.etiq" % namesave
	cmd = "/people/laurent/tvd/monfork/tvd/tvd/algorithms/alignment/align.pl %s %s %s > %s" % (fic, wav, namesave, out)
	os.system(cmd)

	with codecs.open(out, "rt", encoding='utf8') as f:
		for line in f:
			words = line.strip().split()
			tab[words[1]].append(line)

	lastEnd = 0

	os.remove(out)
	os.remove(fic)
	for t1, t2, data in g.ordered_edges_iter(data=True):
		if 'speech' in data:
			cle = "%s-%s" % (t1.T,t2.T)
			speaker = data['speaker']
			lines = tab[cle]
			prevNode = t1
			for line in lines:
				words = line.strip().split()
				mot = words[3]
				m = re.match(r"([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) \(([^ ]+) \- ([^ ]+) \- ([^\)]+)\)", line)
				if m:
					mot = m.group(4)
					start = m.group(5)
					end = m.group(6)
					conf = m.group(7)
					#Je regarde lastEnd (c'est le temps de fin du dernier tour de parole ...)
					#Ne dois jamais arriver mais bon...
					if start < lastEnd:
						start = lastEnd+0.001
					node_start = TAnchored(float(start))
					#prevVal = stringVal(prevNode.T)
					if prevNode.is_anchored and prevNode.T != node_start.T:
						if node_start.T < prevNode.T:
							node_start.T = prevNode.T
						print "Node between %s and %s => no data" % (prevNode, node_start)
						g.add_annotation(prevNode, node_start, data={})
					else:
						if prevNode.is_floating:
							print "Node between %s and %s => no data" % (prevNode, node_start)
							g.add_annotation(prevNode, node_start, data={})

					node_end = TAnchored(float(end))
					if node_end.T <= node_start.T:
						node_end.T = node_start.T+0.001

					print "Node between %s and %s => data{speech:%s speaker:%s confidence:%s}" % (node_start, node_end, mot, speaker, conf)
					g.add_annotation(node_start, node_end, data={'speech':mot, 'speaker':speaker, 'confidence':conf})
					prevNode = node_end
				else:
					#prevVal = stringVal(prevNode.T)
					if prevNode.is_anchored:
						node_start = TAnchored(prevNode.T)
						node_end = TAnchored(prevNode.T+0.001)
						print "Node between %s and %s => data{speech:%s speaker:%s confidence:0.950}" % (node_start, node_end, mot, speaker)
						g.add_annotation(node_start, node_end, data={'speech':mot, 'speaker':speaker, 'confidence':'0.950'})
						prevNode = node_end
			if prevNode.is_anchored:
				print "Node between %s and %s => no data"%(prevNode,t2)
				g.add_annotation(prevNode, t2, data={})
				lastEnd = prevNode.T
	g.save("%s.json" % namesave)
