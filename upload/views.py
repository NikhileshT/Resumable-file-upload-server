from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.core.files.storage import default_storage
import os
from django.core.files.base import ContentFile

temp_base = os.path.expanduser("./tmp/")

def home(request):
    return render(request, 'index.html')

def resumable(request):
    if request.method == 'GET':
        resumableIdentfier = request.GET['resumableIdentifier']
        resumableFilename = request.GET['resumableFilename']
        resumableChunkNumber = request.GET['resumableChunkNumber']

        if not resumableIdentfier or not resumableFilename or not resumableChunkNumber:
            # Parameters are missing or invalid
            abort(500, 'Parameter error')

        # chunk folder path based on the parameters
        temp_dir = os.path.join(temp_base, resumableIdentfier)

        # chunk path based on the parameters
        chunk_file = os.path.join(temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))

        if os.path.isfile(chunk_file):
            # Let resumable.js know this chunk already exists
            return HttpResponse('OK')
        else:
            # Let resumable.js know this chunk does not exists and needs to be uploaded
            abort(404, 'Not found')

    elif request.method == 'POST':
        resumableTotalChunks = request.POST['resumableTotalChunks']
        resumableChunkNumber = request.POST['resumableChunkNumber']
        resumableFilename = request.POST['resumableFilename']
        resumableIdentfier = request.POST['resumableIdentifier']

        # get the chunk data
        chunk_data = request.FILES['file']

        # make our temp directory
        temp_dir = os.path.join(temp_base, resumableIdentfier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir, 0o777)

        # save the chunk data
        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(temp_dir, chunk_name)
        default_storage.save(chunk_file, ContentFile(chunk_data.read()))

        # check if the upload is complete
        chunk_paths = [os.path.join(temp_dir, get_chunk_name(str(resumableFilename), str(x))) for x in range(1, int(resumableTotalChunks)+1)]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:
            target_file_name = os.path.join(temp_base, resumableFilename)
            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    stored_chunk_file_name = p
                    stored_chunk_file = open(stored_chunk_file_name, 'rb')
                    target_file.write(stored_chunk_file.read())
                    stored_chunk_file.close()
                    os.unlink(stored_chunk_file_name)
            target_file.close()
            os.rmdir(temp_dir)

        return HttpResponse('OK')

def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % int(chunk_number)
