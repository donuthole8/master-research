import cv2
from matplotlib import pyplot as plt
from osgeo import gdal
import numpy as np


DIVISION_NUM = 100

def write_tiffile(res,read_file,write_file):
  """
  tifファイルの保存
  """
  # Nodataの消去
  # idx = np.where((res == 0) or (res == 12623735.))
  # res[idx] = -1

  # tif画像テンプレ読み込み
  src = gdal.Open(read_file)

  # 画像サイズ・バンド数
  xsize = int(src.RasterXSize/DIVISION_NUM)
  ysize = int(src.RasterYSize/DIVISION_NUM)
  band = src.RasterCount

  # 第1-4バンド
  b3,b2,b1 = res,res,res
  b4 = src.GetRasterBand(4).ReadAsArray()

  # データタイプ番号（32-bit float）
  dtid = 6

  # 出力画像
  output = gdal.GetDriverByName('GTiff').Create(write_file, xsize, ysize, band, dtid)

  # 座標系指定
  output.SetGeoTransform(src.GetGeoTransform())

  # 空間情報を結合
  output.SetProjection(src.GetProjection())
  output.GetRasterBand(1).WriteArray(b1)
  output.GetRasterBand(2).WriteArray(b2)
  output.GetRasterBand(3).WriteArray(b3)
  # output.GetRasterBand(4).WriteArray(b4)
  output.FlushCache()


# メイン関数
def main():
  # 入力画像読込
  path1 = './images/dsm_uav_raw.tif'
  # path2 = './images/dsm_heli_clipping_raw.tif'
  path2 = './images/koyaura.tif'
  dsm_uav = cv2.imread(path1, cv2.IMREAD_UNCHANGED)
  dsm_heli = cv2.imread(path2, cv2.IMREAD_UNCHANGED)

  # _dsm_uav = cv2.resize(dsm_uav, dsize=(int(dsm_uav.shape[1]/DIVISION_NUM),int(dsm_uav.shape[0]/DIVISION_NUM)))
  # _dsm_heli = cv2.resize(dsm_heli, dsize=(int(dsm_heli.shape[1]/DIVISION_NUM),int(dsm_heli.shape[0]/DIVISION_NUM)))

  # リサイズ
  dsm_koyaura = cv2.resize(dsm_heli, dsize=(int(dsm_uav.shape[1]),int(dsm_uav.shape[0])))

  # _dsm_uav = cv2.resize(dsm_uav, dsize=(int(dsm_heli.shape[1]/DIVISION_NUM),int(dsm_heli.shape[0]/DIVISION_NUM)))

  # print("uav",_dsm_uav.shape)
  # print("heli",_dsm_heli.shape)

  # f = open('uav.txt', 'w')
  # for i in _dsm_uav:
  #   for j in i:
  #     f.write(str(j) + ' ')
  #   f.write(str('\n'))
  # f.close()
  # f = open('heli.txt', 'w')
  # for i in _dsm_heli:
  #   for j in i:
  #     f.write(str(j) + ' ')
  #   f.write(str('\n'))
  # f.close()


  # 航空写真DSMの不要範囲除去（UAVでの透過背景消去）
  # idx = np.where(dsm_koyaura < -300)
  # dsm_uav[idx] = None
  # idx = np.where(_dsm_heli < -300)
  # _dsm_heli[idx] = -4.5

  # # 正規化
  # _max,_min = np.max(_dsm_heli),np.min(_dsm_heli)
  # _dsm_heli = (_dsm_heli-_min)/(_max-_min)
  # _max,_min = np.max(_dsm_uav),np.min(_dsm_uav)
  # _dsm_uav = (_dsm_uav-_min)/(_max-_min)

  # tif画像への書き出し
  # write_tiffile(_dsm_uav, "./images/dsm_uav_img.tif", "test_uav.tif")
  write_tiffile(dsm_koyaura, "./images/dsm_uav_img.tif", "koyaura_resize.tif")


if __name__ == "__main__":
  main()
