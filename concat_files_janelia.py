from omero.rtypes import rint
from omero.gateway import BlitzGateway
from Parse_OMERO_Properties import USERNAME, PASSWORD, HOST, PORT
# from Parse_OMERO_Properties import imageId, datasetId
import sys

# Create a connection
# =================================================================
conn = BlitzGateway(USERNAME, PASSWORD,
                    host=HOST, port=PORT)
conn.connect()
ret = conn.setGroupForSession(long(sys.argv[1]))

# conn.SERVICE_OPTS.setOmeroGroup('-1')

# Retrieve image in specified dataset
# =================================================================

datasetId = sys.argv[2]
# print(datasetId)

dataset = conn.getObject("Dataset", datasetId)
# print(dataset)
nameIds = []
for img in dataset.listChildren():
    if img.getId != datasetId:
        nameIds.append((img.getName(), img.getId()))
# print(nameIds)
nameIds.sort()
# print(nameIds)
imageNames = [x for x, y in nameIds]
imageIds = [y for x, y in nameIds]
# print(imageNames, imageIds)
img = conn.getObject('Image', imageIds[0])
sizeZ, sizeC = img.getSizeT(), img.getSizeC()
dataset = img.getParent()
pixels = img.getPrimaryPixels()

sizeT = 0

uniqueNames = []
uniqueIds = []

for counter in range(len(imageNames)):
    if counter < len(imageNames) - 1:
        if imageNames[counter] != imageNames[counter + 1]:
            sizeT += 1
            uniqueNames.append(imageNames[counter])
            uniqueIds.append(imageIds[counter])
    else:
        sizeT += 1
        uniqueNames.append(imageNames[counter])
        uniqueIds.append(imageIds[counter])
    # print(uniqueNames, uniqueIds)
# sizeT = long(sizeT)
# zctList = []
# for z in range(sizeZ):
#     for c in range(sizeC):
#         for t in range(sizeT):
#             zctList.append((0, c, z))


def planeGen():
    # print("entered planegen, uniqueIds:", uniqueIds)
    pixels = []
    for fileId in uniqueIds:
        # print(fileId)
        original = conn.getObject("Image", fileId)
        pixels.append(original.getPrimaryPixels())
    for z in range(sizeZ):          # all Z sections
        for c in range(sizeC):
            for t in range(sizeT):      # all time-points
                # print("Plane: ", z, c, t)
                yield pixels[t].getPlane(0, c, z)


desc = ("Image created from Image concatenating multiple tiffs")
print(sizeZ, sizeC, sizeT)
new_img = conn.createImageFromNumpySeq(
    planeGen(), "SingleTimelapse", sizeZ, sizeC, sizeT, description=desc,
    dataset=dataset)
