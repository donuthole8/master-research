import cv2,time
from osgeo import gdal,osr
import pymeanshift as pms
from PIL import Image


def read_tifffile(path):
  src = gdal.Open(path)

  xsize = src.RasterXSize
  ysize = src.RasterYSize
  band = src.RasterCount

  # 第1-4バンド
  b1 = src.GetRasterBand(1).ReadAsArray()
  b2 = src.GetRasterBand(2).ReadAsArray()
  b3 = src.GetRasterBand(3).ReadAsArray()
  b4 = src.GetRasterBand(4).ReadAsArray()

  # データタイプ番号
  dtid = src.GetRasterBand(1).DataType

  # 出力画像
  output = gdal.GetDriverByName('GTiff').Create('./results/geo.tif', xsize, ysize, band, dtid)

  # 座標系指定
  output.SetGeoTransform(src.GetGeoTransform())

  # 空間情報を結合
  output.SetProjection(src.GetProjection())
  output.GetRasterBand(1).WriteArray(b1)
  output.GetRasterBand(2).WriteArray(b2)
  output.GetRasterBand(3).WriteArray(b3)
  output.GetRasterBand(4).WriteArray(b4)
  output.FlushCache()
  output = None


def meanshift(img,spatial_radius,range_radius,min_density):
  start = time.time()
  lab_img, _, _ = pms.segment(cv2.cvtColor(img, cv2.COLOR_BGR2Lab), spatial_radius, range_radius,min_density)
  img = cv2.cvtColor(lab_img, cv2.COLOR_Lab2BGR)

  cv2.imwrite('results/meanshift.png',img)

  # PyMeanShift実行時間
  meanshift_time = time.time() - start
  print("meanshift time:{0}".format(meanshift_time) + "[sec]")

  return img


# def image(_org,_img):
#   global org,img,h,w,c
#   global bo,go,ro,al

#   org,img = _org,_img
#   h,w,c = img.shape
#   bo,go,ro = cv2.split(org)
#   al = 0.45


def equalization(img):
  hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  h, s, v = cv2.split(hsv_img)

  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
  new_v = clahe.apply(v)

  hsv_clahe = cv2.merge((h, s, new_v))
  new_rgb_img = cv2.cvtColor(hsv_clahe, cv2.COLOR_HSV2BGR)

  img = new_rgb_img
  cv2.imwrite('results/equalization.png',img)

  return img


def clustering(img):
  img = Image.fromarray(img)
  img_q = img.quantize(colors=128, method=0, dither=1)
  img_q.save('results/clustering.png')
  img = cv2.imread('results/clustering.png', cv2.IMREAD_COLOR)

  img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
  cv2.imwrite('results/clustering.png',img)

  return img


def quantization(img):
  # img = img // 4 * 4
  # img = img // 8 * 8
  img = img // 16 * 16
  cv2.imwrite('results/quantization.png', img)

  return img
