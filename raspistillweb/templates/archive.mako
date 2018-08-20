# -*- coding: utf-8 -*- 
<%inherit file="archive-layout.mako"/>


    
    <div class="navbar navbar-static-top">
        <div class="container">
            <div class="navbar-header">
                <form action="action_picture" method="POST" class="navbar-form" id="form_action">
                    <button type="button" class="btn btn-success" id="selectAll">Select all</button>
                    <div class="form-group">
                        <select name="action" class="form-control" id="availableActions">
                            <option>Select an action...</option>
                            <option value="download">Download</option>
                            
                            % if gdrive_upload :
                            <option value="gdrive">Upload on GDrive</option>
                            % endif
                            
                            <option value="delete">Delete</option>
                        </select>
                        
                        <button type="submit" class="btn btn-danger" id="submitAction">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
      <div class="row">
      % for file in database:     
        <div class="col-xs-6 col-sm-4 col-md-3">
          <div class="panel panel-default">
            <div class="panel-heading">

                <input type="checkbox" name="pic_id" value="${file['id']}" class="close no_opacity">

              <h3 class="panel-title">${file['date']}</h3>
            </div>
            <div class="panel-body">
              <a href="${request.static_url('raspistillweb:pictures/')}${file['filename']}" class="thumbnail img-rounded">
                <img src="${request.static_url('raspistillweb:thumbnails/')}${file['filename']}" alt="${file['filename']}">
              </a> 
              <dl>
                <dt>Resolution</dt>
                <dd>${file['resolution']}</dd>
                <dt>Filesize</dt>
                <dd>${file['filesize']}</dd>
                <dt>Images</dt>
                <dd>
                % for s in file['slaves']:
                    % if s['gdrive'] is not None:
                    <img src='${request.static_url('raspistillweb:static/images')}/gdrive_${s['gdrive'].lower()}.png' title='GDrive Status' alt='GDrive Status'>
                    % endif
                    <a href="${request.static_url('raspistillweb:pictures/')}${s['filename']}">${s['sensor_name']}</a>&nbsp;&nbsp;
                % endfor
                </dd>
              </dl>
            </div>
          </div>     
        </div>   
      % endfor 
      </div>
    </div>
    
    <script type="text/javascript">
    jQuery('#selectAll').on('click',function(){
        jQuery('input[type="checkbox"]').prop('checked',true)
    });
    
    jQuery('#submitAction').on('click',function(e){
        e.preventDefault()
        checkboxes = jQuery('input[type="checkbox"]:checked')
        
        
        if (jQuery('#availableActions option:selected').val() == 'delete')
        {
            var retVal = confirm("Do you really want to delete all the selected images? This operation is PERMANENT!");
            if (retVal == false)
                return;
        }
        
        jQuery('#form_action').append(jQuery(checkboxes))
        
        jQuery('#form_action').submit()
        
    });
    </script>

