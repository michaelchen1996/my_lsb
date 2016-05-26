from PIL import Image
import math
import sys

class R:
    prime_list = [2,3,5,7,11,13,17,19,23,29,
    31,37,41,43,47,53,59,61,67,71,
    73,79,83,89,97,101,103,107,109,113,
    127,131,137,139,149,151,157,163,167,173,
    179,181,191,193,197,199,211,223,227,229,
    233,239,241,251,257,263,269,271,277,281,
    283,293,307,311,313,317,331,337,347,349,
    353,359,367,373,379,383,389,397,401,409,
    419,421,431,433,439,443,449,457,461,463,
    467,479,487,491,499,503,509,521,523,541,
    547,557,563,569,571,577,587,593,599,601,
    607,613,617,619,631,641,643,647,653,659,
    661,673,677,683,691,701,709,719,727,733,
    739,743,751,757,761,769,773,787,797,809,
    811,821,823,827,829,839,853,857,859,863,
    877,881,883,887,907,911,919,929,937,941,
    947,953,967,971,977,983,991,997]

    def __init__(self, num):
        self.number = num
        # 确定P Q block_num N
        a = self.getChildren(self.number)
        self.P = a.pop()
        self.Q = self.P
        while (self.Q==self.P):
            self.Q = a.pop()
        self.N = self.P*self.Q
        self.block_num = self.number//(self.P*self.Q)

        # 确定 D E
        self.D = self.getD((self.P-1)*(self.Q-1))
        self.E = self.getE((self.P-1)*(self.Q-1),self.D)

    def __init__(self, w, h, key = 0):
        # 确定P Q
        self.P = self.getP(w)
        self.Q = self.getQ(h)
        self.N = self.P*self.Q
        # 确定 D E
        self.D = self.getD((self.P-1)*(self.Q-1))
        self.E = self.getE((self.P-1)*(self.Q-1),self.D)
        # 初始化矩阵
        self.matrix = [0 for i in range(w*h)]
        self.key = key


    def getw(self):
        return self.P

    def geth(self):
        return self.Q

    def getP(self, w):
        while w:
            if self.isprime(w):
                return w
            w -= 1

    def getQ(self, h):
        while h:
            if self.isprime(h) and h != self.P:
                return h
            h -= 1

    def isprime(self, x):
        for i in range(2, int(math.sqrt(x))+1):
            if x % i == 0:
                return False
        return True

    def getChildren(self, num):
        i = 2
        l = []
        while i <= num:
            if num % i == 0:
                l.append(i)
                num = num / i
                i = 2
            else:
                i += 1
            if num == 1:
                break
        return l

    def gcd(self, a, b):
        if b == 0:
            return a
        else:
            return self.gcd(b, a % b)

    def getD(self, a):
        for i in self.prime_list:
            if self.gcd(i,a) == 1:
                return i

    def getE(self,a,b):
        for i in range(10000000000):
            if (a*i+1)%b==0:
                return (a*i+1)//b

    # C=(A EXP D) mod N
    def encodeX(self, x):
        block = x//self.N
        A = x%self.N
        C = pow(A, self.D)%self.N
        return C+block*self.N

    # A=(C EXP E) mod N
    def decodeX(self, x):
        block = x//self.N
        C = x%self.N
        A = pow(C, self.E)%self.N
        return A+block*self.N

    def shuffle(self, x, position):
        size = self.getw() * self.geth()
        pos = (x + position) % size
        if self.matrix[pos] is 0:
            self.matrix[pos] = 1
        else:
            while self.matrix[pos]:
                pos += 1
                if pos == size:
                    pos = 0
        self.matrix[pos] = 1
        return self.encodeX(pos)

#end class R

class MY_LSB:
    # 取出来的数据都放在这里
    dump_data = bytearray(0)

    # 构造时打开指定图片文件
    def __init__(self, image_name):
        self.im = Image.open(image_name)
        self.w, self.h = self.im.size
        self.band_num = len(self.im.getbands())
        # 创建加密类的实例
        self.r = R(self.w, self.h)
        # 修改有效的隐写区域
        self.w = self.r.getw()
        self.h = self.r.geth()

    # 打开隐写文件，在encode时使用
    def open_file(self, file_name):
        self.file = open(file_name, "rb")
        self.file_data = self.file.read()
        self.file.close()
        self.data_len = len(self.file_data)
        # 判断大小是否合适
        if self.data_len > self.h * self.w * self.band_num:
            print("File is toooooooo large!")
            exit(1)

    # 从文件的第index位读取数据
    def get_file_bit(self, index):
        if index < self.data_len * 8:
            return self.file_data[index // 8] >> (7 - index % 8) & 0x1;
        else:
            if index == self.data_len * 8:
                return 1;
            else:
                return 0

    # 把数据写到文件的第index位
    def put_file_bit(self, index, value):
        # 若为一个字节的第一位，先增加一个字节
        if index % 8 == 0:
            self.dump_data.append(0)
        # 写到相应字节的相应位中
        self.dump_data[index // 8] = self.dump_data[index // 8] << 1 & 0xff | value

    # 通过prev和pos得到下一个隐写位置（像素点）
    def get_pos(self, pos, prev):
        (x, y) = pos
        temp = self.r.shuffle(prev, y * self.w + x)
        #print("%d -> %d" % (index, temp))
        return (temp % self.w, temp // self.w)

    # 隐写操作
    def encode(self, file_name, out_image_name):
        self.open_file(file_name)
        # 遍历有效隐写区的每一个像素
        for index in range(0, self.w * self.h):
            # 定义初始pos和prev
            if index==0:
                pos = (0, 0)
                prev = 0
            # 找到下一个隐写位置
            pos = self.get_pos(pos, prev)
            # 获取像素
            pixel = list(self.im.getpixel(pos))
            # 在像素的各层中（例如R、G、B）进行最低位写入
            for k in range(0, self.band_num):
                # 最低位掩码掩去，和数据进行或运算
                pixel[k] = pixel[k] & 0xfe | self.get_file_bit(index * self.band_num + k)
                # prev在原有基础上和新的像素异或
                prev ^= pixel[k]
            # 隐写后的像素写回图片
            self.im.putpixel(pos, tuple(pixel))
        # 隐写后图片保存
        self.im.save(out_image_name)

    # 恢复操作，操作基本相同，因此注释基本同上
    def decode(self, file_name):
        for index in range(0, self.w * self.h):
            if index==0:
                pos = (0, 0)
                prev = 0
            pos = self.get_pos(pos, prev)
            pixel = list(self.im.getpixel(pos))
            for k in range(0, self.band_num):
                # 通过掩码把最低有效位取出到文件
                self.put_file_bit(index * self.band_num + k, pixel[k] & 0x1)
                prev ^= pixel[k]
        # dump_data写入文件中
        temp = len(self.dump_data) - 1
        while self.dump_data[temp]==0:
            temp -= 1
        file = open(file_name, "wb")
        file.write(self.dump_data[0:temp])
        file.close()

#MY_LSB("AM.jpg").encode("hide.txt", "a.bmp")
#MY_LSB("a.bmp").decode("a.txt")

# 主函数入口
if __name__ == '__main__':
    # 判断encode情况
    if len(sys.argv)==5 and sys.argv[1]=="encode":
        # 得到三个文件名字符串
        # 载体文件名
        image_file_name = sys.argv[2]
        # 需要隐藏（写入载体）的文件名
        in_file_name = sys.argv[3]
        # 输出文件名
        out_file_name = sys.argv[4]
        # 新建实例执行encode
        MY_LSB(image_file_name).encode(in_file_name, out_file_name)
    else:
        # 判断decode情况
        if len(sys.argv)==4 and sys.argv[1]=="decode":
            # 得到三个文件名字符串
            # 输入文件名
            in_file_name = sys.argv[2]
            # 提取到的信息输出文件名
            out_file_name = sys.argv[3]
            # 新建实例执行decode
            MY_LSB(in_file_name).decode(out_file_name)
        else:
            # 对错误输入进行格式提醒
            print("""error: invalid syntax
python3 my_lsb.py
    encode <image> <in> <out>
    decode <in> <out>""");


