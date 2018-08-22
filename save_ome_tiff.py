from omero.rtypes import rint
from omero.gateway import BlitzGateway
from Parse_OMERO_Properties import USERNAME, PASSWORD, HOST, PORT
# from Parse_OMERO_Properties import imageId, datasetId
import sys
import os
import omero.util.script_utils as script_utils
from omero.constants.namespaces import NSCREATED, NSOMETIFF


conn = BlitzGateway(USERNAME, PASSWORD,
                    host=HOST, port=PORT)
conn.connect()
ret = conn.setGroupForSession(long(sys.argv[1]))

datasetId = sys.argv[2]
imageId = sys.argv[3]

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


new_img = conn.getObject('Image', imageId)
dataset = conn.getObject("Dataset", datasetId)
save_as_ome_tiff(conn, new_img)

folder_name = ""
exp_dir = ""
#ometiff_ids = [t.id for t in dataset.listAnnotations(ns=NSOMETIFF)]
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
