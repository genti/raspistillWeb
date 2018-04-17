# -*- coding: utf-8 -*- 
<%inherit file="settings-layout.mako"/>

<%!
def float_numbers(num):
    return "%.4f" % num
%>

<div class="container">
 
  
  <div id="calibration_progress">
    <div class="col-md-10 col-md-offset-1">
      
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">${device}: ${timestamp}</h3>
        </div>
        <div class="panel-body">
          <dl>
            <dt>Matrix</dt>
            <dd>
            
            <table class="table table-bordered" >
            % for r in mtx:
            <tr>
                % for c in r:
                    <td>${float_numbers(c)}</td>
                % endfor
            </td>
            % endfor
            </table>
            
            </dd>
            <dt>Distortion vector</dt>
            <dd><table class="table table-bordered" >
            <tr>
                % for c in range(len(dist[0])):
                    <td>${float_numbers(dist.flatten()[c])}</td>
                % endfor
            </td>
            </table>
            </dd>
            <dt>Rotation vector</dt>
            <dd><table class="table table-bordered" >
            % for r in rvecs:
            <tr>
                % for c in range(len(r)):
                    <td>${float_numbers(r.flatten()[c])}</td>
                % endfor
            </td>
            % endfor
            </table>
            </dd>
            <dt>Translation vector</dt>
            <dd><table class="table table-bordered" >
            % for r in tvecs:
            <tr>
                % for c in range(len(r)):
                    <td>${float_numbers(r.flatten()[c])}</td>
                % endfor
            </td>
            % endfor
            </table>
            </dd>
          <dl>
        </div>
    </div>
  </div>  
  
</div>

<script src="${request.static_url('raspistillweb:static/js/calibration.js')}"></script>

