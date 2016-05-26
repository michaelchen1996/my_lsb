# my_lsb
### 概要
my_lsb是一个通过LSB算法实现信息隐藏的Python程序。具有将文件写入图片和从写入文件的图片中提取文件的功能。其中使用伪随机算法和RSA加密算法进行位置变换，保证文件机密性

### 运行环境
- Python3
- Pillow

### 使用方法
	
	# 隐藏文件
	# 后3个参数：载体图片、需要隐藏的文件、隐藏后的图片 的文件名
	python3 my_lsb.py encode <image> <in> <out>
	
	# 提取文件
	# 后2个参数：隐藏后的图片、提取出的文件 的文件名
	python3 my_lsb.py decode <in> <out>