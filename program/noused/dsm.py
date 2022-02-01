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
  path1 = './images/seaarea.tif'

  dsm_uav = cv2.imread(path1,0)

  print(dsm_uav)


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


  # tif画像への書き出し
  write_tiffile(dsm_sub,"./images/dsm_heli_resize_img.tif")



if __name__ == "__main__":
  main()

