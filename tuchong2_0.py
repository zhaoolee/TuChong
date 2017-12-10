import requests
import json
import re
import time
import os
from multiprocessing import Process, Queue
import time
from time import sleep
import threading
import sys
import random

class TuChong(object):
	def __init__(self):

		self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
		self.target_image_num = 0
		self.title_name = None
		self.q_json = Queue()
		self.q_album = Queue()
		self.q_image = Queue()

		pass

	# 负责获取响应
	def get_response_content(self, url):
		try:
			response = requests.get(url, headers = self.headers)
			return response.content
		except:
			pass

	def get_json_data(self):

		title =["风光","人像","城市","旅行","纪实","街拍","人文","美女","建筑","静物","夜景","自然","少女","儿童","秋天","光影","花卉","私房","色彩","抓拍","黑白","小清新","情绪","日系","后期","写真","微距","创意","情感","复古","手机","佳能","尼康","胶片","索尼","50mm","35mm","广角","富士","iphone","宾得","85mm","北京","上海","广州",
"深圳","南京","成都","武汉","厦门","杭州","重庆","西藏","西安","四川","大连","新疆","长沙","苏州","日本","中国","浙江","川西","香港","云南","青岛"]

		for i in range(len(title)):
			if i%5 == 0:
				print()
			print("{""代号", i,"-->",title[i],"}",end="")

		print("")
		print("=="*10)	

		while True:
			try:
				title_code = int(input("请输入代号:"))
				if 0<=title_code<=65:
					break
				else:
					print("请重新输入数字!")
			except Exception as e:
				print("输入的非数值,请重新输入")


		self.title_name = title[title_code]

		while True:
			try:
				self.target_image_num = int(input("请输入图片数量:"))
				if self.target_image_num > 0:
					break
				else:
					print("请输入正整数!")
			except:
				print("输入的图片数量非数值类型,请重新输入")



		print("开始下载-->%s主题"%(self.title_name))
		# 获取json数据
		for m in range(1, 300):
			tc_get_json = "https://tuchong.com/rest/tags/%s/posts?page=%s&count=60"%(self.title_name,m)
			# print("获取json:",tc_get_json)
			try:
				tc_json = self.get_response_content(tc_get_json)

			except:
				continue

			self.q_json.put(tc_json)


	def get_album_url(self):
		while True:
			try:
				str_data = self.q_json.get().decode()

			except Exception as e:
				# print("-->获取json数据失败",e)
				sleep(0.1)
				continue

			try:

				page_list_jsons = json.loads(str_data)["postList"]
				# print("page_list_json","-->", len(page_list_jsons))
				if len(page_list_jsons) == 0:
					break
			except Exception as e:
				pass

			for page_list_json in page_list_jsons:

				temp = {}
				# 获取图集主题
				try:
					temp["title"] = page_list_json["title"]
					# print("-->获得图集名称-->",temp["title"])
					# 获取图集url
					temp["url"] = page_list_json["url"]
				except Exception as e:
					# print("获取图集信息出错",e)
					pass
				# 过滤帖子类型的图集
				if re.match(r"https://tuchong.com/(\d)*?/(\d)*?/", temp["url"]):
					# 将url与标题,信息加入队列
					self.q_album.put(temp)
					# 记录图集的url

					with open("./图集源目录.txt", "a") as f:
						t = page_list_json["title"]
						u = page_list_json["url"]
						log = t+"-->"+u+"\n"
						# print("已预解析文案",log)
						f.write(log)


	# 根据图集获取单张图片url地址
	def get_image_url(self):

		while True:
			sleep(0.1)

			# 获取图集url和标题
			try:
				album = self.q_album.get()
			except Exception as e:
				print("正在获取图集首页...")
				continue
			album_url = album["url"]
			album_title = album["title"]
			# 获取图集首页响应内容
			response_content = self.get_response_content(album_url)
			# 获取图集图片集合信息
			image_info_list = re.findall(r'\"img_id\"\:\d+\,\"user_id\"\:\d+', response_content.decode())

			for image_info in image_info_list:
				img_id = image_info.split(",")[0].split(":")[1]
				user_id = image_info.split(",")[1].split(":")[1]
				image_url = "https://photo.tuchong.com/%s/f/%s.jpg"%(user_id, img_id)
				# 将图片url信息和所在的图集标题加入队列
				temp = dict()
				temp["image_url"] = image_url
				temp["album_title"] = album_title
				temp["album_url"] = album_url

				self.q_image.put(temp)
				# print("-->put",temp)


	def save_image(self):
		while True:
			
			# sleep(0.1)

			try:
				# 获取图片信息
				image_temp = self.q_image.get()
			except Exception as e:
				# print("准备下载图片")
				continue
			image_url = image_temp["image_url"]
			album_title = image_temp["album_title"]
			album_url = image_temp["album_url"]
			old_name = re.match(r".*?f\/(.*)",image_url).group(1)
			new_image_name = album_title +"_"+old_name

			# 建立文件夹
			try:
				os.makedirs("./images/%s"%(self.title_name))
			except Exception as e:
				pass

			# 写入图片
			file_path = "./images/%s/%s"%(self.title_name, new_image_name)

			
			if self.target_image_num <= 0:
				print("下载完毕")
				sys.exit()
			try:
				# 生成1至2秒的随机数
				random_time_sec = random.randint(1, 2)

				if os.path.exists(file_path):
					# print("重复跳过")
					continue
				time.sleep(random_time_sec)
				
				print("模拟延时(学羊叫):",random_time_sec,"秒")
				
				image_data = self.get_response_content(image_url)
				with open(file_path, "wb+") as f:
					print("正在下载第%d张图片.."%(self.target_image_num))
					self.target_image_num -= 1
					with open("./影集目录.txt", "a")as z:
						now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
						log = album_title + "-->" +album_url+ " | 下载时间:" +now_time + "\n"
						z.write(log)

					print("-->", file_path, image_url)

					f.write(image_data)

			except:
				# print("网络故障,图片下载变慢")
				pass





def main():
	tuchong = TuChong()

	t0 = threading.Thread(target=tuchong.get_json_data)


	t1 = threading.Thread(target=tuchong.get_album_url)


	t2 = threading.Thread(target=tuchong.get_image_url)


	try:
		t3 = threading.Thread(target=tuchong.save_image)
		t3.start()
		# print("t3开始")

	except:
		print("主程序退出")
		sys.exit()

	t2.start()
	# print("t2开始")

	t1.start()
	# print("t1开始")

	t0.start()
	# print("t0开始")

if __name__ == '__main__':
	main()