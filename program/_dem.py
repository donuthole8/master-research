import cv2,os
from matplotlib import pyplot as plt
from osgeo import gdal,osr
import numpy as np

# tif画像のりサイズ
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
#   output = gdal.GetDriverByName('GTiff').Create('./results/dem_uav_resize.tif', xsize, ysize, band, dtid)

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
  output = gdal.GetDriverByName('GTiff').Create('./results/dem_sub.tif', xsize, ysize, band, dtid)

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
  path1 = 'images/dem_uav_img.tif'
  path2 = 'images/dem_gsi_resize_img.tif'
  if not os.path.isfile(path1 or path2):
    raise FileNotFoundError('Image file not found!')
  dem_uav = cv2.imread(path1,0)
  dem_gsi = cv2.imread(path2,0)

  print(dem_uav.shape)
  print(dem_gsi.shape)

  # ドローンDEMのリサイズ
  dem_uav = cv2.resize(dem_uav, dsize=(dem_gsi.shape[1],dem_gsi.shape[0]))
  cv2.imwrite("./results/dem_uav_resize.png", dem_uav)

  # バイナリ書き出し
  f = open('./binary/dem_uav_resize.txt', 'w')
  for i in dem_uav:
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()

  # サイズ確認・画素値確認
  print(dem_uav.shape)
  print(dem_gsi.shape)
  print(dem_uav)
  print(dem_gsi)

  # DEMの差分算出
  dem_sub = dem_uav - dem_gsi
  # UAVのDEMで0値は透過背景
  idx = np.where(dem_uav == 0)
  dem_sub[idx] = 0
  cv2.imwrite("./results/dem_sub.png", dem_sub)

  # ヒストグラム算出
  # plt.hist(dem_uav.ravel(),bins=256,range=[1,256],histtype="bar",rwidth=0.5,color="teal")
  # plt.savefig("./histogram/dem_uav.png")

  # plt.hist(dem_gsi.ravel(),bins=256,range=[10,256],histtype="bar",rwidth=0.5,color="darkred")
  # plt.savefig("./histogram/dem_gsi.png")

  plt.hist(dem_uav.ravel(),bins=256,range=[10,256],histtype="step",rwidth=0.5,color="teal",log=True)
  plt.hist(dem_gsi.ravel(),bins=256,range=[10,256],histtype="step",rwidth=0.5,color="darkred",log=True)
  plt.savefig("./histogram/uav&gsi.png")

  # plt.hist(dem_uav.ravel(),bins=256,range=[2,10],histtype="step",rwidth=0.5,color="teal",log=True)
  # plt.hist(dem_gsi.ravel(),bins=256,range=[2,10],histtype="step",rwidth=0.5,color="darkred",log=True)
  # plt.savefig("./histogram/uav&gsi.png")

  # plt.hist(dem_sub.ravel(),bins=256,range=[1,256],histtype="bar",rwidth=0.5,color="darkred")
  # plt.savefig("./histogram/dem_sub.png")


  # バイナリ書き出し
  f = open('./binary/dem_sub.txt', 'w')
  for i in dem_sub:
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()

  # tif画像のリサイズ
  # resize_tiffile(dem_gsi.shape[1],dem_gsi.shape[0],"./images/dem_uav.tif")

  # tif画像への書き出し
  write_tiffile(dem_sub,"./images/dem_gsi_resize_img.tif")



if __name__ == "__main__":
  main()

