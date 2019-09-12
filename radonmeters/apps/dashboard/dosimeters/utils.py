

# import zipfile
# from django.http import HttpResponse



# def _generate_reports_pdf(dosimeter):
#     data_set = []

#     file_name = 'report_[%s]' % dosimeter.serial_number

#     data_set.append({
#         'file_name': '%s.pdf' % file_name,
#         'file_data': dosimeter.dosimeter_pdf_report_generate()})

#     return data_set

# def _return_pdf(data_set):

#         # Prepare data.
#     file_name = data_set['file_name']
#     file_data = data_set['file_data']

#     if file_data is None:
#     	return HttpResponse('<h1>Error Rendering Pdf</h1>')
#     # Prepare and return response.
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
#     response.write(file_data)
#     return response
