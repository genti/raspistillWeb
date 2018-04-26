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
              <li>${alert}</li>  
            % endfor
          </ul>
        </div>
      </div>
    </div>
  % endif
  <div class="row">
    <div class="col-md-10 col-md-offset-1">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">Preferences</h3>
        </div>
        <div class="panel-body">
          <form action="save" method="POST" class="form-horizontal" role="form">
            <div class="form-group">
              <label class="col-lg-2 control-label">Device Name</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" placeholder="${hostName}" title="Name used to identify this Phenotiki device in a network." readonly>
              </div>
            </div>
            
            <span class="help-block">Image preferences:</span>
            
            <div class="form-group">
              <label for="imageResolution1" class="col-lg-2 control-label">Image Resolution</label>
              <div class="col-sm-3">
                <select name="imageResolution" class="form-control" id="imageResolution1">
                  <option selected>${image_width}x${image_height}</option>
                    % for resolution in image_resolutions:
                      % if resolution != image_width + 'x' + image_height:                               
                        <option>${resolution}</option>
                      % endif
                    % endfor
                </select>
              </div>
              <div class="col-sm-1 text-center">
                <label for="imageResolution2" class="control-label">or</label>
              </div>
              
              <div class="col-md-4 col-lg-3 col-sm-4">
                <div class="input-group">
                  <span class="input-group-addon"><span class="glyphicon glyphicon-resize-horizontal"></span></span>
                  <input type="number" class="form-control" name="imageWidth" min="1" max="3280" placeholder="${image_width}" title="Set custom width (pixels).">
                </div>
              </div>
              <div class="col-md-4 col-lg-3 col-sm-4">
                <div class="input-group">
                  <span class="input-group-addon"><span class="glyphicon glyphicon-resize-vertical"></span></span>
                  <input type="number" class="form-control" name="imageHeight" min="1" max="2464" placeholder="${image_height}" title="Set custom height (pixels).">
                </div>                
              </div>
            </div>
            
            <div class="form-group">
              <label for="ecodingMode1" class="col-lg-2 control-label">Encoding Mode</label>
              <div class="col-lg-10">
                <select name="encodingMode" class="form-control" id="encodingMode1">
                  % for mode in encoding_modes:
                    % if mode == encoding_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="isoOption1" class="col-lg-2 control-label">ISO Option</label>
              <div class="col-lg-10">
                <select name="isoOption" class="form-control" id="isoOption1">
                  % for option in iso_options:
                    % if option == image_iso:
                      <option selected>${option}</option>
                    % else:
                      <option>${option}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="exposureMode1" class="col-lg-2 control-label">Exposure Mode</label>
              <div class="col-lg-10">
                <select name="exposureMode" class="form-control" id="exposureMode1">
                  % for mode in exposure_modes:
                    % if mode == exposure_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="imageEffect1" class="col-lg-2 control-label">Image Effect</label>
              <div class="col-lg-10">
                <select name="imageEffect" class="form-control" id="imageEffect1">             
                  % for effect in image_effects:
                    % if effect == image_effect:
                      <option selected>${effect}</option>
                    % else:
                      <option>${effect}</option>
                    % endif
                  % endfor
                </select>
              </div>  
            </div>
            
            <div class="form-group">
              <label for="awbMode1" class="col-lg-2 control-label">AWB Mode</label>
              <div class="col-lg-10">
                <select name="awbMode" class="form-control" id="awbMode1">             
                  % for mode in awb_modes:
                    % if mode == awb_mode:
                      <option selected>${mode}</option>
                    % else:
                      <option>${mode}</option>
                    % endif
                  % endfor
                </select>
              </div>  
            </div>
            
            <div class="form-group">
              <label for="imageRotation1" class="col-lg-2 control-label">Image Rotation</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if image_rotation == '0' else ''}">
                    <input type="radio" name="imageRotation" value="0" ${'checked' if image_rotation == '0' else ''}><span class="glyphicon glyphicon-circle-arrow-up"></span> 0°
                  </label>
                  <label class="btn btn-default ${'active' if image_rotation == '90' else ''}">
                    <input type="radio" name="imageRotation" value="90" ${'checked' if image_rotation == '90' else ''}><span class="glyphicon glyphicon-circle-arrow-right"></span> 90°
                  </label>
                  <label class="btn btn-default ${'active' if image_rotation == '180' else ''}">
                    <input type="radio" name="imageRotation" value="180" ${'checked' if image_rotation == '180' else ''}><span class="glyphicon glyphicon-circle-arrow-down"></span> 180°
                  </label>
                  <label class="btn btn-default ${'active' if image_rotation == '270' else ''}">
                    <input type="radio" name="imageRotation" value="270" ${'checked' if image_rotation == '270' else ''}><span class="glyphicon glyphicon-circle-arrow-left"></span> 270°
                  </label>
                </div>
              </div>  
            </div>
            
            
            <div class="form-group">
              <label for="imageResolution1" class="col-lg-2 control-label">HDR</label>
              <div class="col-sm-4">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if hdr_enabled == 'Yes' else ''}" title="Enable HDR">
                    <input type="radio" name="hdrEnabled" value="Yes" ${'checked' if hdr_enabled == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if hdr_enabled == 'No' else ''}" title="Disable HDR.">
                    <input type="radio" name="hdrEnabled" value="No" ${'checked' if hdr_enabled == 'No' else ''}> No
                  </label>
                </div>
              </div>  
              
              <div class="col-sm-6">
                <div class="input-group">
                  <input type="text" class="form-control" name="exposureTimes" value="${hdr_exposure_times}" placeholder="1000;500;250" title="Set custom exposur times.">
                  <span class="input-group-addon">Exposure times</span>
                </div>                
              </div>
            </div>
        
            
            
            <div class="form-group">
              <label for="NumberImages1" class="col-lg-2 control-label">Number of shots</label>
              <div class="col-lg-10">
                <div class="input-group">
                  <input type="number" class="form-control" id="NumberImages1" name="numberImages" min="1" value="${number_images}" title="Number of pictures to acquire">
                  <span class="input-group-addon">shots</span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="CommandBeforeAcquisition1" class="col-lg-2 control-label">Command before acquisition</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="CommandBeforeAcquisition1" name="commandBeforeAcquisition" value="${command_before_sequence}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="CommandAfterAcquisition1" class="col-lg-2 control-label">Command after acquisition</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="CommandAfterAcquisition1" name="commandAfterAcquisition" value="${command_after_sequence}">
              </div>
            </div>
            
             <div class="form-group">
              <label for="CommandBeforeShot1" class="col-lg-2 control-label">Command before shot</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="CommandBeforeShot1" name="commandBeforeShot" value="${command_before_shot}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="CommandAfterShot1" class="col-lg-2 control-label">Command after shot</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="CommandAfterShot1" name="commandAfterShot" value="${command_after_shot}">
              </div>
            </div>
            
            <span class="help-block">Timelapse preferences:</span>
            
            <div class="form-group">
              <label for="TimelapseInterval1" class="col-lg-2 control-label">Interval</label>
              <div class="col-lg-10">
                <div class="input-group">
                  <input type="number" class="form-control" id="TimelapseInterval1" name="timelapseInterval" min="1" value="${timelapse_interval}" title="Time (seconds) between image acquisitions.">
                  <span class="input-group-addon">secs</span>
                </div>
                <!--<input type="number" class="form-control" id="TimelapseInterval1" name="timelapseInterval" placeholder="${timelapse_interval}">-->
              </div>
            </div>
            
            <div class="form-group">
              <label for="TimelapseTime1" class="col-lg-2 control-label">Event Duration</label>
              <div class="col-lg-10">
                <div class="input-group">
                  <input type="number" class="form-control" id="TimelapseTime1" name="timelapseTime" min="1" value="${timelapse_time}" title="Total duration (seconds) of the time-lapse acquisition.">
                  <span class="input-group-addon">secs</span>
                </div>
                <!--<input type="number" class="form-control" id="TimelapseTime1" name="timelapseTime" placeholder="${timelapse_time}">-->
              </div>
            </div>
            
            <span class="help-block"><h4>Bisque preferences:</h4></span>
            
            <div class="form-group">
              <label for="BisqueEnabled1" class="col-lg-2 control-label">Bisque Sync</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if bisque_enabled == 'Yes' else ''}" title="Transmit acquired images to Bisque.">
                    <input type="radio" name="bisqueEnabled" value="Yes" ${'checked' if bisque_enabled == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if bisque_enabled == 'No' else ''}" title="Acquired images are not transmitted to Bisque.">
                    <input type="radio" name="bisqueEnabled" value="No" ${'checked' if bisque_enabled == 'No' else ''}> No
                  </label>
                </div>
              </div>  
            </div>
            
            <div class="form-group">
              <label for="BisqueUser1" class="col-lg-2 control-label">Username</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="BisqueUser1" name="bisqueUser" value="${bisque_user}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="BisquePswd1" class="col-lg-2 control-label">Password</label>
              <div class="col-lg-10">
                <input type="password" class="form-control" id="BisquePswd1" name="bisquePswd" value="${bisque_pswd}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="BisqueRootUrl1" class="col-lg-2 control-label">Bisque Root URL</label>
              <div class="col-lg-10">
                <input type="url" class="form-control" id="BisqueRootUrl1" name="bisqueRootUrl" value="${bisque_root_url}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="BisqueLocalCopy1" class="col-lg-2 control-label">Keep Local Copy</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if bisque_local_copy == 'Yes' else ''}" title="Keep a copy of image files on the device.">
                    <input type="radio" name="bisqueLocalCopy" value="Yes" ${'checked' if bisque_local_copy == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if bisque_local_copy == 'No' else ''}" title="Delete images from the device after transmission to Bisque.">
                    <input type="radio" name="bisqueLocalCopy" value="No" ${'checked' if bisque_local_copy == 'No' else ''}> No
                  </label>
                </div>
              </div>  
            </div>

        <span class="help-block"><h4>Google Drive preferences:</h4></span>
            
            <div class="form-group">
              <label for="gdriveEnabled1" class="col-lg-2 control-label">Gdrive Upload</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if gdrive_enabled == 'Yes' else ''}" title="Transmit acquired images to Google Drive.">
                    <input type="radio" name="gdriveEnabled" value="Yes" ${'checked' if gdrive_enabled == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if gdrive_enabled == 'No' else ''}" title="Acquired images are not transmitted to Google Drive.">
                    <input type="radio" name="gdriveEnabled" value="No" ${'checked' if gdrive_enabled == 'No' else ''}> No
                  </label>
                </div>
              </div>  
            </div>
        
       <span class="help-block">Go to <a href="http://console.developers.google.com" target="_blank">Google Developer Console</a> to get your Client ID and Secret Token.</span>
       
       <div class="form-group">
              <label for="GdriveFolder1" class="col-lg-2 control-label">Google Drive Upload Folder</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="GdriveFolder1" name="gdriveFolder" value="${gdrive_folder}">
              </div>
           </div>

           <div class="form-group">
              <label for="GdriveUser1" class="col-lg-2 control-label">Google Drive Client ID</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="GdriveUser1" name="gdriveUser" value="${gdrive_user}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="GdriveSecret1" class="col-lg-2 control-label">Google Drive Secret Token</label>
              <div class="col-lg-10">
                <input type="text" class="form-control" id="GdriveSecret1" name="gdriveSecret" value="${gdrive_secret}">
              </div>
            </div>
            
            <div class="form-group">
              <label for="BisqueEnabled1" class="col-lg-2 control-label">Delete files</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if gdrive_file_delete == 'Yes' else ''}" title="Delete files in GDrive.">
                    <input type="radio" name="gdriveDelete" value="Yes" ${'checked' if gdrive_file_delete == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if gdrive_file_delete == 'No' else ''}" title="Keep always GDrive files.">
                    <input type="radio" name="gdriveDelete" value="No" ${'checked' if gdrive_file_delete == 'No' else ''}> No
                  </label>
                </div>
              </div>  
            </div>
            <span class="help-block">Delete files in G-Drive when they are deleted locally.</span>
            
            <span class="help-block"><h4>Multisensor trigger:</h4></span>
            
            <div class="form-group">
              <label for="multisensor" class="col-lg-2 control-label">Multisensor</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if multisensor_enabled == 'Yes' else ''}" title="Tiggers multiple Phenotiki sensors at the same time.">
                    <input type="radio" name="multisensorEnabled" value="Yes" ${'checked' if multisensor_enabled == 'Yes' else ''}> Enabled
                  </label>
                  <label class="btn btn-default ${'active' if multisensor_enabled == 'No' else ''}" title="Tiggers multiple Phenotiki sensors at the same time.">
                    <input type="radio" name="multisensorEnabled" value="No" ${'checked' if multisensor_enabled == 'No' else ''}> Disabled
                  </label>
                </div>
              </div>  
            </div>
            
            <div class="form-group">
              <label for="asyncDownload" class="col-lg-2 control-label">Async download</label>
              <div class="col-lg-10">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default ${'active' if async_download == 'Yes' else ''}" title="Asynchronous download of images from other devices">
                    <input type="radio" name="asyncDownload" value="Yes" ${'checked' if async_download == 'Yes' else ''}> Yes
                  </label>
                  <label class="btn btn-default ${'active' if async_download == 'No' else ''}" title="Asynchronous download of images from other devices">
                    <input type="radio" name="asyncDownload" value="No" ${'checked' if async_download == 'No' else ''}> No
                  </label>
                </div>
              </div>  
            </div>
            
            <script>
                jQuery('input[name=asyncDownload][value=Yes]').change(function(){
                    if (jQuery(this).is(':checked')){
                        alert('By activating this option, a reboot is necessary');
                    }
                })
            </script>
            
            <div class="form-group">
              <label for="GdriveSecret1" class="col-lg-2 control-label">Sensors name:</label>
              <div class="col-lg-10">
                <textarea rows="5" cols="50" class="form-control" id="sensors_name" name="sensors_name">${sensors_name}</textarea>
              </div>
            </div>           
            
            <div class="form-group">
                % if len(clients)>0:
                <span class="help-block col-lg-2">Connected Clients:</span>
                <ul class="col-lg-10">
                    % for c in clients:
                        <li>${c['ip']} &dash; ${c['mac']}</li>
                    % endfor
                </ul>
                % endif
            </div>
            
            <span class="help-block"><h4>Camera calibration:</h4></span>
            <span class="help-block">Go to the <a href="/camera_calibr">Camera Calibration Tool</a>.</span>
            
            
            
            <div class="form-group">
              <div class="col-lg-offset-2 col-lg-10">
                <button type="submit" formmethod="POST" class="btn btn-primary">Save</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div> 
</div>
