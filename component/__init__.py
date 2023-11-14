import sys
import os

res = os.path.dirname(os.path.abspath(__file__))
res = "/".join(res.split('/')[0:-2])
# print(res)
sys.path.append(res)
