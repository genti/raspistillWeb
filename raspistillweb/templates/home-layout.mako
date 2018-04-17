# -*- coding: utf-8 -*- 
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>${project}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${request.static_url('raspistillweb:static/css/bootstrap.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_url('raspistillweb:static/css/bootstrap-responsive.css')}" rel="stylesheet">
    <link href="${request.static_url('raspistillweb:static/css/customizations.css')}" rel="stylesheet">
    
  </head>
  <body>

    <div class="navbar navbar-inverse navbar-static-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="http://phenotiki.com" target="_blank">Phenotiki</a>
        </div>
        <div class="navbar-collapse collapse" style="height: 1px;">
          <ul class="nav navbar-nav">
            <li class="active"><a href="/">Home</a></li>
            <li><a href="/settings">Settings</a></li>
            <li><a href="/archive">Archive</a></li>
            <li><a href="/timelapse">Time Lapse</a></li>
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false"><span class="glyphicon glyphicon-off" aria-label="Shutdown"></span> <span class="caret"></span></a>
              <ul class="dropdown-menu">
                <li><a href="/reboot"><span class="glyphicon glyphicon-repeat" aria-hidden="true"></span> Reboot</a></li>
                <li><a href="/shutdown"><span class="glyphicon glyphicon-off" aria-hidden="true"></span> Shutdown</a></li>
              </ul>
            </li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <li><h3 class='async_download ${'hidden' if downloadInProgress == False else ''}'><span class='label label-info'>&#8681;</span></h3></li>
            <li>
              <form method="post">
                <input type="button" class="btn btn-danger navbar-btn" value="Take Photo" onclick="location.href='/photo'">
              </form>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    ${next.body()} 
    
    <script src="${request.static_url('raspistillweb:static/js/jquery.min.js')}"></script>
    <script src="${request.static_url('raspistillweb:static/js/bootstrap.min.js')}"></script>
  
  </body>
</html>
