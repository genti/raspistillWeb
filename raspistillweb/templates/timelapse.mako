# -*- coding: utf-8 -*- 
<%inherit file="timelapse-layout.mako"/>

<div class="container">
  <div class="row">
    % if timelapse:
      <div class="col-md-12">
        <div class="alert alert-danger">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
          <p><strong>Time-lapse in progress.</strong> Refresh the page to update the progress bar.</p>
          <div class="progress">
            <div class="progress-bar" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="width: ${percentage_completed}%;">${percentage_completed}%</div>
          </div>
          Please wait until the time-lapse acquisition has finished or press the button below to stop the process.
          <button type="button" class="btn btn-danger btn-sm" onclick="location.href='/timelapse_stop'">Stop Time-lapse</button>
        </div>
      </div>
    % else:
    <div class="col-md-12">
      <div class="panel panel-default">
        <div class="panel-heading">
            <h3 class="panel-title">Time-lapse</h3>
          </div>
          <div class="panel-body">
            There is currently no time-lapse in progress.<br />You can start a time-lapse acquisition with the following preferences or change them on the <a href="/settings"><strong>Settings</strong></a> page.
            <dl>
              <dt>Interval</dt>
              <dd>${timelapseInterval} s</dd>
              <dt>Duration</dt>
              <dd>${timelapseTime} s</dd>
            </dl>
            <form method="post">
              <input type="button" class="btn btn-danger btn-lg" value="Start time-lapse" onclick="location.href='/timelapse_start'">
            </form>
          </div>
      </div>
    </div>
    % endif    
  </div>
  <div class="row">
  % for file in timelapseDatabase:     
    <div class="col-xs-6 col-sm-4 col-md-3">
      <div class="panel panel-default">
        <div class="panel-heading">
          <form action="delete_timelapse" method="POST">
            <button type="submit" name="id" value="${file['id']}" class="close">&times;</button>
          </form>
          <h3 class="panel-title">${file['timeStart']}</h3>
        </div>
        <div class="panel-body">
          <dl>
            <dt>Number of Images</dt>
            <dd>${file['n_images']}</dd>
            <dt>Image Resolution</dt>
            <dd>${file['resolution']}</dd>
            <dt>Encoding Mode</dt>
            <dd>${file['encoding_mode']}</dd>
            <dt>Exposure Mode</dt>
            <dd>${file['exposure_mode']}</dd>
            <dt>Image Effect</dt>
            <dd>${file['image_effect']}</dd>
            <dt>AWB Mode</dt>
            <dd>${file['awb_mode']}</dd>
            <dt>Start</dt>
            <dd>${file['timeStart']}</dd>
            <dt>End</dt>
            <dd>${file['timeEnd']}</dd>
          </dl>
          <a href="${request.static_url('raspistillweb:time-lapse/')}${file['filename']}.zip"><button type="button" class="btn btn-success btn-sm btn-block">Download</button></a>
        </div>
      </div>     
    </div>   
  % endfor  
  </div>  
</div>
