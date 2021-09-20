import numpy as np
from osgeo import gdal, gdalconst
from osgeo import osr # 空間参照モジュール

src = gdal.Open('./images/_koyaura.tif')

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

# 空間参照情報
srs = osr.SpatialReference()

# 空間情報を結合
output.SetProjection(src.GetProjection())
output.GetRasterBand(1).WriteArray(b1)
output.GetRasterBand(2).WriteArray(b2)
output.GetRasterBand(3).WriteArray(b3)
output.GetRasterBand(4).WriteArray(b4)
output.FlushCache()
output = None
