import json
import time
import os
import re
import hashlib
#pip install xpinyin
from xpinyin import Pinyin


path = "data"
log = "log.txt"
outf = "rdf_triplet.txt"
outf_neo4j_node = "neo4j_nodes.txt"
outf_neo4j_edge = "neo4j_edges.txt"

def get_current_time():
    return time.strftime('%Y-%m-%d %X', time.localtime(time.time()))

def clean(s):
	return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\r", "").replace(",", "，")

def hash_digest(s):
        return "h_%s" % hashlib.sha256(s).hexdigest()

def get_initial_letter(ch):
	if ch=="":
		return ""

	#get rid of the "，" in ch
	ch = ch.replace("，", "").replace(",", "").replace("、", "")

	pin = Pinyin()	
	test = pin.get_pinyin(ch, "-")

	ret_str = ""
	pinyin_arr = test.split("-")
	for item in pinyin_arr:
		ret_str += item[0]
	
	return ret_str

def get_val(dict, key):
	if key in dict.keys() and clean(dict[key]) != "缺":
		return clean(dict[key])
	else:
		return ""

def get_name_gender_birthday(s):
	arr = s.split(" ")
	ret_arr = []
	for item in arr:
		if item.strip() != "":
			ret_arr.append(item)
	#it's a triky here
	while len(ret_arr) < 3:
		ret_arr.append(" ")

	return ret_arr


def load_log(log):
	f_s = set()
	if os.path.exists(log):
		with open(log) as indata:
			for line in indata:
				f_s.add(line.strip().split()[0])
	return f_s

def write_into_file(f, content):
	with open(f, 'a+') as f:
		f.write("%s\n" % content)


relate1 = "治疗"
relate2 = "组成"
node_dise = "疾病"
node_pres = "方剂"
node_herb = "草药"
node_s = set()
edge_s = set()

fd = open(outf, "w+", encoding='UTF-8')
fd_node = open(outf_neo4j_node, "w+", encoding='UTF-8')
fd_edge = open(outf_neo4j_edge, "w+", encoding='UTF-8')

fd_node.write("node:ID,name,:LABEL\n")
fd_edge.write(":START_ID,:END_ID,:TYPE\n")
#print(path)
#logf = load_log(log)
for root, dirs, files in os.walk(path):
	for file in files:
		#if file in logf:
		#	continue
		jsonfile = os.path.join(root, file)
		print(jsonfile)


		#exit(0)
		cnt = 0
		values_str = ""
		#jsonfile = "医案+曹玉山.txt"
		#with open(jsonfile, 'r', encoding='UTF-8') as indata:
		with open(jsonfile, 'r') as indata:
			json_dict = json.load(indata)
			print("total records: %s" % len(json_dict))

			for key,rcd in json_dict.items():
				#print(rcd)

				t = get_current_time()
				case_title = rcd['医案标题']
				doctor_name = rcd['医生姓名']
				department = rcd['科别']
				patient_name = ""
				gender = ""
				birth_day = ""
				patient_name, gender, birth_day = get_name_gender_birthday(rcd['医案']['患者姓名'])

				treatment_time = get_val(rcd['医案'], '就诊时间')
				solar_term = get_val(rcd['医案'], '节气')
				patient_description = get_val(rcd['医案'], '主诉')
				current_illness_history = get_val(rcd['医案'], '现病史')
				tongue_symptom = "%s; %s" % (get_val(rcd['医案'], '舌质'), get_val(rcd['医案'], '舌苔'))
				pulse_symptom = get_val(rcd['医案'], '脉象')
				current_symptom = get_val(rcd['医案'], '刻下症')
				illness_history = get_val(rcd['医案'], '既往史')
				personal_history = get_val(rcd['医案'], '个人史')
				allergy_history = get_val(rcd['医案'], '过敏史')
				marriage_history = get_val(rcd['医案'], '婚育史')
				family_history = get_val(rcd['医案'], '家族史')
				assist_exam = get_val(rcd['医案'], '辅助检查')
				symptom_analysis = get_val(rcd['医案'], '辨证分析')
				tcm_diagnosis = get_val(rcd['医案'], '中医诊断')
				wm_diagnosis = get_val(rcd['医案'], '西医诊断')
				tcm_syndrome = get_val(rcd['医案'], '中医证候')
				therapeutic = get_val(rcd['医案'], '治则治法')
				prescription = get_val(rcd['医案'], '方名')
				composition = get_val(rcd['医案'], '组成')
				usages = get_val(rcd['医案'], '用法')
				doctor_comments = get_val(rcd['医案'], '医嘱')
				acupuncture = get_val(rcd['医案'], '针灸')
				point_select = get_val(rcd['医案'], '选穴')
				massage = get_val(rcd['医案'], '推拿')

				#get the unique name of the prescription
				if prescription.strip() == "":
					prescription = "方剂"
				prescription_name = "%s_%s" % (prescription, get_initial_letter(case_title))
				#
				#prescription_name = prescription_name.encode("UTF-8")
				#tcm_diagnosis = tcm_diagnosis.encode("UTF-8")

				trip1 = "%s %s %s" % (prescription_name, tcm_diagnosis, relate1)
				print(trip1)
				fd.write("%s\n" % trip1)

				if prescription_name not in node_s:
					fd_node.write("%s,%s,%s\n" % (hash_digest(prescription_name.encode("UTF-8")), prescription_name, node_pres))
					node_s.add(prescription_name)
				if tcm_diagnosis not in node_s:
					fd_node.write("%s,%s,%s\n" % (hash_digest(tcm_diagnosis.encode("UTF-8")), tcm_diagnosis, node_dise))
					node_s.add(tcm_diagnosis)
				edge_str = "%s,%s,%s\n" % (hash_digest(prescription_name.encode("UTF-8")), hash_digest(tcm_diagnosis.encode("UTF-8")), relate1)
				if edge_str not in edge_s:
					fd_edge.write(edge_str)
					edge_s.add(edge_str)

				medicine_arr = composition.split("，")
				for item in medicine_arr:
					arr = re.split(r'\d+', item)
					herb = arr[0]
					#herb = herb.encode("UTF-8")
					trip2 = "%s %s %s" % (prescription_name, herb, relate2)
					print(trip2)
					fd.write("%s\n" % trip2)

					if herb not in node_s:
						fd_node.write("%s,%s,%s\n" % (hash_digest(herb.encode("UTF-8")), herb, node_herb))
						node_s.add(herb)
					edge_str = "%s,%s,%s\n" % (hash_digest(prescription_name.encode("UTF-8")), hash_digest(herb.encode("UTF-8")), relate2)
					if edge_str not in edge_s:
						fd_edge.write(edge_str)
						edge_s.add(edge_str)

				#break
				cnt += 1
			print("get records: %s" % cnt)

			#log this file
			#write_into_file(log, "%s %s" % (file, cnt))
fd.close()
fd_node.close()
fd_edge.close()
