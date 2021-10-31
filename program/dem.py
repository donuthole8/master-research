import cv2,os
from matplotlib import pyplot as plt
from osgeo import gdal,osr
import numpy as np



def read_tifimage(path1,path2,name):
  """
  tifファイルの保存
  path1:tif画像のrawデータパス
  path2:tif画像の画像データパス
  name:uavとgsiの指定
  """

  # tif画像（raw形式）読み込み
  raw = cv2.imread(path1,cv2.IMREAD_UNCHANGED)
  # tif画像（画像形式）読み込み
  src = gdal.Open(path2)

  # 横・縦・バンド数（数値）
  xsize = src.RasterXSize
  ysize = src.RasterYSize
  band = src.RasterCount

  # 第1-4バンド（2次元配列）
  b1 = src.GetRasterBand(1).ReadAsArray()
  b2 = src.GetRasterBand(2).ReadAsArray()
  b3 = src.GetRasterBand(3).ReadAsArray()
  b4 = src.GetRasterBand(4).ReadAsArray()

  # バイナリ出力
  f = open(f'./binary/{name}_raw.txt', 'w')
  for i in raw:
    for j in i:
      f.write(str(int(j)) + ' ')
    f.write(str('\n'))
  f.close()

  f = open(f'./binary/{name}_img.txt', 'w')
  for i in cv2.imread(path2,cv2.IMREAD_GRAYSCALE):
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()

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

  return raw,output



def clip_gsi_raw(uav_raw,gsi_raw):
  # 国土地理院DEMの不要範囲除去
  idx = np.where(uav_raw == -32767.0)
  gsi_raw[idx] = -999

  return gsi_raw



def draw_histogram(uav_raw,gsi_raw,name):
  # ヒストグラム比較
  plt.clf()
  if (name=="_normalization"):
    hist_range=[-2,334]
  else:
    hist_range=[-135,147]
  plt.hist(uav_raw.ravel(),bins=256,range=hist_range,histtype="step",rwidth=0.5,color="teal",label="uav")
  plt.hist(gsi_raw.ravel(),bins=256,range=[-2,334],histtype="step",rwidth=0.5,color="darkred",label="gsi")
  plt.ylim(0,1800)
  plt.savefig(f"./histogram/uav&gsi{name}.png")

  cv2.imwrite("./results/dem_gsi_clipping.png",gsi_raw)



def  normalize_dem_uav(uav_raw,gsi_raw):
  # 最大・最小値算出（-32767はNo Dataであるため除く）
  max_uav,min_uav = np.max(uav_raw),np.unique(uav_raw)[1]
  max_gsi,min_gsi = np.max(gsi_raw),np.unique(gsi_raw)[1]
  # 標高値がヒストグラム上で重なるように手動設定
  # min_uav = -36

  # 標高最大値（山間部の頂上・植生頂上）の変化は無いと仮定する
  # （標高最小値（海・海岸）は海抜0mと仮定する）
  # UAVのDEMを0 - 333mに正規化
  _uav_raw = (uav_raw-min_uav)/(max_uav-min_uav) * max_gsi
  idx = np.where(_uav_raw == -21779.332)
  _uav_raw[idx] = -999

  # バイナリ出力
  f = open(f'./binary/normalization.txt', 'w')
  for i in _uav_raw:
    for j in i:
      f.write(str(int(j)) + ' ')
    f.write(str('\n'))
  f.close()

  # 正規化画像保存
  cv2.imwrite("./results/normalization.png",_uav_raw)

  return _uav_raw


def write_tifimage(res,path):
  """
  tifファイルの保存
  res:tifファイルに保存するデータ
  path:雛形tifファイルのパス
  """

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

  #  衛星データの特定の値をnodataにする　－gdal_translate－ 　
# ・オプション [-a_nodata] を使う 　
# gdal_translate -a_nodata [value] [input file name] [output file name] 　






# メイン関数
def main():
  # 入力画像読込
  path1 = 'images/dem_uav_raw.tif'
  path2 = 'images/dem_gsi_raw.tif'
  path3 = 'images/dem_uav_img.tif'
  path4 = 'images/dem_gsi_img.tif'
  if not os.path.isfile(path1 or path2 or path3 or path4):
    raise FileNotFoundError('Image file not found!')

  # tif画像からの読み込み
  uav_raw,uav_tif = read_tifimage(path1,path3,"uav")
  gsi_raw,gsi_tif = read_tifimage(path2,path4,"gsi")

  # 国土地理院DEMの範囲切り抜き
  clipping_gsi_raw = clip_gsi_raw(uav_raw,gsi_raw)

  # ヒストグラム描画
  draw_histogram(uav_raw,clipping_gsi_raw,"")

  # UAVのDEMの標高値調整
  normalization_uav_raw = normalize_dem_uav(uav_raw,clipping_gsi_raw)

  # ヒストグラム描画
  draw_histogram(normalization_uav_raw,gsi_raw,"_normalization")

  # 差分処理
  dem_sub = normalization_uav_raw - clipping_gsi_raw
  # UAVのDEMで0値は透過背景
  idx = np.where(uav_raw == -32767.0)
  dem_sub[idx] = -999
  cv2.imwrite("./results/dem_sub.png", dem_sub)

  # tif画像への書き出し
  write_tifimage(dem_sub,path3)



if __name__ == "__main__":
  main()

