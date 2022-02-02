import cv2,os
import preprocessing
import analysis
import detection
import drawing


# 入力画像読込
# path = 'images/_koyaura.tif'
path = 'images/koyaura.tif'

if not os.path.isfile(path):
	raise FileNotFoundError('Image file not found!')
img = cv2.imread(path, cv2.IMREAD_COLOR)
print(int(img.shape[0]), 'x', int(img.shape[1]), 'pix')


# サイズ縮小
# per = 0.5
# height,width = img.shape[0],img.shape[1]
# print(int(height*per),' x ',int(width*per),'pix')
# img = cv2.resize(img , (int(width*per), int(height*per)))

# デバッグモード
# import pdb; pdb.set_trace()

# オリジナル画像保存
org = img.copy()
cv2.imwrite('results/original.png', org)

# PyMeanShift
#   - Lab変換後の画像に適用
#   - 第１引数：探索範囲、第２引数：探索色相、第３引数：粗さ
# img = preprocessing.meanshift(img,10,10,300)
img = cv2.imread('./images/clustering.png', cv2.IMREAD_COLOR)
# img = cv2.imread('./images/meanshift.png', cv2.IMREAD_COLOR)

# DSMマスク用にリサイズ
img = cv2.resize(img, dsize=(7369,6871))
org = cv2.resize(img, dsize=(7369,6871))

# # ヒストグラム均一化
# #   - Lab変換して処理した方が好ましい
# #   - 明度以外のチャンネルも均一化した方が好ましい
# img = preprocessing.equalization(img)

# # 量子化・減色処理・ノイズ除去
# #   - 領域分割後に類似領域に異色画素が散在してるため行う
# img = preprocessing.quantization(img)

# img = cv2.medianBlur(img, 5)
# cv2.imwrite('results/median.png', img)

# img = cv2.bilateralFilter(img, 9, 75, 75)
# cv2.imwrite('results/bilateral.png', img)

# # 類似色統合（DSM用に消した）
# img = preprocessing.clustering(img)

# 着目色（64色に減色）ごとに二値化（着目色とそれ以外、白黒ラベリングする）、そいで次の色に写って、、、、繰り返し
# 白黒ラベリング
# analysis.labeling(img,qua)

# テクスチャ解析
#   - img か org のどちらに適用するか関数内で選択
# methods.texture(img)
# methods.texture(org)

# エッジ抽出
#   - img か org のどちらに適用するか関数内で選択
# analysis.edge(img)
# analysis.edge(org)

# img = detection.correction_shadow(org, img)
# img = detection.correction_whiteout(org, img)

# 災害領域検出
_lnd = detection.detection(org, img)

# 不要領域検出
_veg = detection.rejection(org, img)

# 最終出力
res = drawing._integration(_lnd,_veg,org)
drawing.write_tiffile(res,path)


# 精度評価
#   - 領域単位で評価
#   - 国土地理院の斜面崩壊判読図と比較もあり
#   - 本手法ではピクセルベースでの精度評価
# postpro.evaluation(_lnd,_fld)
