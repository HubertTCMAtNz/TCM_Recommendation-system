#!/usr/bin/env python
import sys
import hashlib

def hash_digest(s):
        return "h_%s" % hashlib.sha256(s).hexdigest()

def enc_str(s):
        return s.replace("\\","\\\\")

def get_state(domain, dic):
	#print type(dic),domain
	if not dic.has_key(domain):
		return "U"
	return dic[domain]

if len(sys.argv) < 5:
	print "{} <node-edge-input-file> <ground-truth-file> <outfile-neo4j-graph-nodes> <outfile-neo4j-graph-edges>".format(sys.argv[0])
	exit(-1)

inf = sys.argv[1]
gtf = sys.argv[2]
outf1 = sys.argv[3]
outf2 = sys.argv[4]

print "loading ground truth file.."
gt_dict = {}
with open(gtf) as indata:
	for line in indata:
		domain, stat = line.strip().split()[0:2]
		gt_dict[domain] = stat


print "output node and edge info.."
label = "Node"
fd1 = open(outf1, "w+")
fd1.write("nodeId:ID,name,state,:LABEL\n")

ty="EDGE"
fd2 = open(outf2, "w+")
fd2.write(":START_ID,:END_ID,weight:float,:TYPE\n")
with open(inf) as indata:
	#domain-domain edge file
	print "Input file is a domain-domain edge file."
	d_set = set()
	for line in indata:
		domain1, domain2, weight = line.strip().split()[0:3]
		#print domain1, domain2
		#output the nodes
		if domain1 not in d_set:
			stat = get_state(domain1, gt_dict)
			fd1.write("{},{},{},{}\n".format(hash_digest(domain1), enc_str(domain1), stat, label))
			d_set.add(domain1)
		if domain2 not in d_set:
			stat = get_state(domain2, gt_dict)
			fd1.write("{},{},{},{}\n".format(hash_digest(domain2), enc_str(domain2), stat, label))
			d_set.add(domain2)

		#output the edges
		fd2.write("{},{},{},{}\n".format(hash_digest(domain1), hash_digest(domain2), weight, ty))
fd1.close()
fd2.close()
print "Done!"


