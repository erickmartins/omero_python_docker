from omero.rtypes import rint
from omero.gateway import BlitzGateway
from Parse_OMERO_Properties import USERNAME, PASSWORD, HOST, PORT
# from Parse_OMERO_Properties import imageId, datasetId
import sys
import os
import omero.util.script_utils as script_utils
from omero.constants.namespaces import NSCREATED, NSOMETIFF

# Create a connection
# =================================================================
conn = BlitzGateway(USERNAME, PASSWORD,
                    host=HOST, port=PORT)
conn.connect()
ret = conn.setGroupForSession(long(sys.argv[1]))

# conn.SERVICE_OPTS.setOmeroGroup('-1')

# Retrieve image in specified dataset
# =================================================================


def save_as_ome_tiff(conn, image, folder_name=None):
    """
    Saves the image as an ome.tif in the specified folder
    """

    extension = "ome.tif"
    name = os.path.basename(image.getName())
    iid = image.getId()
    img_name = "%s-%d.%s" % (name, iid, extension)
    if folder_name is not None:
        img_name = os.path.join(folder_name, img_name)
    # check we don't overwrite existing file
    i = 1
    path_name = img_name[:-(len(extension) + 1)]
    while os.path.exists(img_name):
        img_name = "%s_(%d).%s" % (path_name, i, extension)
        i += 1

    print("  Saving file as: %s" % img_name)
    file_size, block_gen = image.exportOmeTiff(bufsize=65536)
    with open(str(img_name), "wb") as f:
        for piece in block_gen:
            f.write(piece)


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
    # print(pixels)
    for z in range(sizeZ):          # all Z sections
        # print(z)
        for c in range(sizeC):
            # print(c)
            for t in range(sizeT):      # all time-points
                print("Plane: ", z, c, t)
                # print(pixels[t].getPlane(0, c, z))
                yield pixels[t].getPlane(0, c, z)


desc = ("Image created from concatenating multiple tiffs")
print(sizeZ, sizeC, sizeT)
new_img = conn.createImageFromNumpySeq(
    planeGen(), "SingleTimelapse", sizeZ, sizeC, sizeT, description=desc,
    dataset=dataset)

save_as_ome_tiff(conn, new_img)

folder_name = ""
exp_dir = ""
ometiff_ids = [t.id for t in dataset.listAnnotations(ns=NSOMETIFF)]
#conn.deleteObjects("Annotation", ometiff_ids)
extension = "ome.tif"
name = os.path.basename(new_img.getName())
iid = new_img.getId()
img_name = "%s-%d.%s" % (name, iid, extension)
export_file = img_name
namespace = NSOMETIFF
output_display_name = "OME-TIFF"
mimetype = 'image/tiff'

file_annotation, ann_message = script_utils.create_link_file_annotation(
    conn, export_file, dataset, output=output_display_name,
    namespace=namespace, mimetype=mimetype)
