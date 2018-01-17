if response.error != 200:
    output_list['error'] = response.error.message
    print(response.error.message)
    session['image'] = '/static/uploads/default_340x340.jpg'
else:
    labels = response.label_annotations
    for label in labels:
        label_list.append(label.description)
        print(label.description, label.score)
        output_list['labels'] = label_list
        output_list['error'] = ''
print(output_list)
return output_list

< form
role = "form"
action = "/"
method = "POST" >
< dl >
{{imagelinkform.csrf_token}}
{{render_field(imagelinkform.image_link)}}
{{imagelinkform.imagelinksubmit(class_="btn btn-primary")}}
< / dl >
< / form >