import cv2,os
from matplotlib import pyplot as plt
from osgeo import gdal,osr
import numpy as np

# tif画像のリサイズ
# def resize_tiffile(x,y,path):
#   src = gdal.Open(path)

#   xsize = x
#   ysize = y
#   band = src.RasterCount

#   # 第1-4バンド
#   b1 = src.GetRasterBand(1).ReadAsArray()
#   b2 = src.GetRasterBand(2).ReadAsArray()
#   b3 = src.GetRasterBand(3).ReadAsArray()
#   b4 = src.GetRasterBand(4).ReadAsArray()

#   # データタイプ番号
#   dtid = src.GetRasterBand(1).DataType

#   # 出力画像
#   output = gdal.GetDriverByName('GTiff').Create('./results/dsm_uav_resize.tif', xsize, ysize, band, dtid)

#   # 座標系指定
#   output.SetGeoTransform(src.GetGeoTransform())

#   # 空間情報を結合
#   output.SetProjection(src.GetProjection())
#   output.GetRasterBand(1).WriteArray(b1)
#   output.GetRasterBand(2).WriteArray(b2)
#   output.GetRasterBand(3).WriteArray(b3)
#   output.GetRasterBand(4).WriteArray(b4)
#   output.FlushCache()



def write_tiffile(res,path):
  src = gdal.Open(path)

  xsize = src.RasterXSize
  ysize = src.RasterYSize
  band = src.RasterCount

  # 第1-4バンド
  b3,b2,b1 = res,res,res
  b4 = src.GetRasterBand(4).ReadAsArray()

  # データタイプ番号
  dtid = src.GetRasterBand(1).DataType

  # 出力画像
  output = gdal.GetDriverByName('GTiff').Create('./results/dsm_sub.tif', xsize, ysize, band, dtid)

  # 座標系指定
  output.SetGeoTransform(src.GetGeoTransform())

  # 空間情報を結合
  output.SetProjection(src.GetProjection())
  output.GetRasterBand(1).WriteArray(b1)
  output.GetRasterBand(2).WriteArray(b2)
  output.GetRasterBand(3).WriteArray(b3)
  output.GetRasterBand(4).WriteArray(b4)
  output.FlushCache()



# メイン関数
def main():
  # 入力画像読込
  path1 = './images/dsm_uav_img.tif'
  path2 = './images/dms_heli_img.tif'
  src = gdal.Open(path1)
  print(src)

  dsm_uav = cv2.imread(path1,0)
  dsm_heli = cv2.imread(path2,0)

  print(dsm_uav.shape)
  print(dsm_heli.shape)

  # ドローンDSMのリサイズ
  dsm_uav = cv2.resize(dsm_uav, dsize=(dsm_heli.shape[1],dsm_heli.shape[0]))
  cv2.imwrite("./results/dsm_uav_resize.png", dsm_uav)

  # バイナリ書き出し
  f = open('./binary/dsm_uav_resize.txt', 'w')
  for i in dsm_uav:
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()

  # サイズ確認・画素値確認
  print(dsm_uav.shape)
  print(dsm_heli.shape)
  print(dsm_uav)
  print(dsm_heli)

  # DSMの差分算出
  dsm_sub = dsm_uav - dsm_heli
  # UAVのDSMで0値は透過背景
  idx = np.where(dsm_uav == 0)
  dsm_sub[idx] = 0
  cv2.imwrite("./results/dsm_sub.png", dsm_sub)

  # ヒストグラム算出
  # plt.hist(dsm_uav.ravel(),bins=256,range=[1,256],histtype="bar",rwidth=0.5,color="teal")
  # plt.savefig("./histogram/dsm_uav.png")

  # plt.hist(dsm_heli.ravel(),bins=256,range=[10,256],histtype="bar",rwidth=0.5,color="darkred")
  # plt.savefig("./histogram/dsm_heli.png")

  plt.hist(dsm_uav.ravel(),bins=256,range=[10,256],histtype="step",rwidth=0.5,color="teal",log=True)
  plt.hist(dsm_heli.ravel(),bins=256,range=[10,256],histtype="step",rwidth=0.5,color="darkred",log=True)
  plt.savefig("./histogram/uav&heli.png")

  # plt.hist(dsm_uav.ravel(),bins=256,range=[2,10],histtype="step",rwidth=0.5,color="teal",log=True)
  # plt.hist(dsm_heli.ravel(),bins=256,range=[2,10],histtype="step",rwidth=0.5,color="darkred",log=True)
  # plt.savefig("./histogram/uav&heli.png")

  # plt.hist(dsm_sub.ravel(),bins=256,range=[1,256],histtype="bar",rwidth=0.5,color="darkred")
  # plt.savefig("./histogram/dsm_sub.png")


  # バイナリ書き出し
  f = open('./binary/dsm_sub.txt', 'w')
  for i in dsm_sub:
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()

  # tif画像のリサイズ
  # resize_tiffile(dsm_heli.shape[1],dsm_heli.shape[0],"./images/dsm_uav.tif")

  # tif画像への書き出し
  write_tiffile(dsm_sub,"./images/dsm_heli_resize_img.tif")



if __name__ == "__main__":
  main()

