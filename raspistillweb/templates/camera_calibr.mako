# -*- coding: utf-8 -*- 
<%inherit file="settings-layout.mako"/>

<div class="container">
  % if preferences_success_alert:
    <div class="row">
      <div class="col-md-10 col-md-offset-1">
        <div class="alert alert-success alert-dismissable">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Success!</strong> Settings saved. Please follow <a href="/photo" class="alert-link">this link</a> to take a photo.
        </div>
      </div>
    </div>
  % endif
  % if preferences_fail_alert != []: 
    <div class="row">
      <div class="col-md-10 col-md-offset-1">
        <div class="alert alert-danger alert-dismissable">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <strong>Error!</strong> <br>
          <ul>
            % for alert in preferences_fail_alert:
              <li>${alert | n}</li>  
            % endfor
          </ul>
        </div>
      </div>
    </div>
  % endif
  
  <div class="row hidden" id="calibration_progress">
    <div class="col-md-10 col-md-offset-1">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Calibration in progress...</h3>
        </div>
        <div class="panel-body">
        <h1 class="timer"></h1>
        
        <div class="form-group">
            <div class="col-lg-offset-2 col-lg-10">
                <button type="button" class="btn btn-danger" id="stop_calibration">Stop</button>
            </div>
        </div>
        </div>
      </div>
    </div>
  </div>
     
  
  <div class="row">
    <div class="col-md-10 col-md-offset-1">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Calibrate camera</h3>
        </div>
        <div class="panel-body">
          <form action="/camera_calibr_do_pic" method="POST" class="form-horizontal" role="form" id="camera_calibr_form">
            <div class="form-group">
              <label class="col-lg-2 control-label">Device</label>
              <div class="col-lg-10">
                <select name="device" class="form-control" id="device">
                <option value="">Master</option>
                % for device in slaves:
                    <option value="${device['ip']}">${device['name']}</option>
                % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="NumberImages1" class="col-lg-2 control-label">Number of shots</label>
              <div class="col-lg-10">
                <div class="input-group">
                  <input type="number" class="form-control" id="NumberImages" name="numberImages" min="1" value="${number_images}" title="Number of pictures to acquire">
                  <span class="input-group-addon">images</span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="TimelapseInterval1" class="col-lg-2 control-label">Interval</label>
              <div class="col-lg-10">
                <div class="input-group">
                  <input type="number" class="form-control" id="TimelapseInterval1" name="interval" min="1" value="${interval}" title="Time (seconds) between image acquisitions.">
                  <span class="input-group-addon">secs</span>
                </div>
              </div>
            </div>
            
            
                      
            <div class="form-group">
              <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" formmethod="POST" class="btn btn-primary">Acquire images</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div> 
  
  % if calibration_images:
  <div class="row">
    <div class="col-md-10 col-md-offset-1">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Calibration patterns</h3>
        </div>
        
        <div class="panel-body">
          <form action="/camera_calibr_do_calibr" method="POST" class="form-horizontal" role="form" id="camera_calibr_do_calibr">
            <table class="table table-hover">
                <thead>
                    <th>Device</th>
                    <th># images</th>
                    <th>Actions</th>
                </thead>
                <tbody>
                    
                    % for row in calibration_images:
                    <%
                        try:
                            for i in range(len(calibration_images[row])):
                                fname = calibration_images[row][i]
                                if (fname in detected_checkerboards.keys()):
                                    result = 'success' if detected_checkerboards[fname]==True else 'danger'
                                    calibration_images[row][i] = "<span class='label label-%s'>%s</span>"%(result,fname)
                            
                        except:
                            pass
                    %>
                    <tr>
                        <td class="device-name">${row}</td>
                        <td>${', '.join(calibration_images[row]) | n }</td>
                        <td>
                            <button type="submit" name="action" class="btn btn-info calibr-btn" value="detect">Detect Boards</button>
                            <button type="submit" name="action" class="btn btn-success calibr-btn" value="calibr">Calibrate</button>
                            <button type="submit" name="action" class="btn btn-danger calibr-btn" value="delete">Delete</button>
                        </td>
                    </tr>
                    % endfor
                </tbody>
            </table>
          
            <div class="form-group">
              <label for="imageWidth" class="col-lg-2 control-label">Checkerboard size</label>
              <div class="col-md-4 col-lg-3 col-sm-4">
                <div class="input-group">
                  <span class="input-group-addon"><span class="glyphicon glyphicon-resize-horizontal"></span></span>
                  <input type="number" class="form-control" name="checkerHoriz" min="1" max="100" value="${checker_horizontal}" title="Number of horizontal checkers">
                </div>
              </div>
              <div class="col-md-4 col-lg-3 col-sm-4">
                <div class="input-group">
                  <span class="input-group-addon"><span class="glyphicon glyphicon-resize-vertical"></span></span>
                  <input type="number" class="form-control" name="checkerVert" min="1" max="100" value="${checker_vertical}" title="Number of vertical checkers">
                </div>                
              </div>
            </div>
            <input type="hidden" name="client" value="">
          </form>
        </div>
      </div>
    </div>
  </div>
  
  % endif
  
  
  % if parameters:
  <div class="row">
    <div class="col-md-10 col-md-offset-1">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Calibrated cameras</h3>
        </div>
        
        <div class="panel-body">
          <form action="/camera_calibrated_action" method="POST" class="form-horizontal" role="form" id="calibrated_cameras">
            <table class="table table-hover">
                <thead>
                    <th>Device</th>
                    <th>Timestamp</th>
                    <th>Actions</th>
                </thead>
                <tbody>
                    
                    % for c in parameters:

                    <tr>
                        <td class="device-name"><span class="calibration-id">${c.id}</span>&nbsp;${c.device}</td>
                        <td>${c.timestamp}</td>
                        <td>
                            <button type="submit" name="action" class="btn btn-info calibr-btn" value="view">View</button>
                            <button type="submit" name="action" class="btn btn-success calibr-btn" value="apply">Apply</button>
                            <button type="submit" name="action" class="btn btn-danger calibr-btn" value="delete">Delete</button>
                        </td>
                    </tr>
                    % endfor
                </tbody>
            </table>
            
            
            <div class="form-group">
              <label class="col-lg-2 control-label">Picture:</label>
              <div class="col-lg-10">
                <select name="pic_filename" class="form-control" id="pic_filename">
                <option value="0">Select image to rectify...</option>
                % for d in pic_filenames.keys():
                <optgroup label="${d}">
                    % for f in pic_filenames[d]:
                        <option>${f}</option>
                    % endfor
                </optgroup>
                % endfor
                </select>
              </div>
            </div>
          

            <input type="hidden" name="id" value="">
          </form>
        </div>
      </div>
    </div>
  </div>
  
  % endif
  
  
</div>

<script src="${request.static_url('raspistillweb:static/js/calibration.js')}"></script>

