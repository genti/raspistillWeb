var camera_calibr_timer=0
var camera_calibr_pic_taken=0
var camera_calibr_interval_handler=false;
var camera_calibr_lock = false;


$(document).on('submit','form#camera_calibr_form',function(){
        
    init_camera_calibration($(this))
    return false;
})

$('form#camera_calibr_do_calibr button.calibr-btn').on('click',function(e){
    var client = $(this).parents('tr').find('td.device-name').html()
    
    $('form#camera_calibr_do_calibr  input[name="client"]').val(client)

    
})

$('form#calibrated_cameras button.calibr-btn').on('click',function(e){
    var id = $(this).parents('tr').find('td.device-name').find('span.calibration-id').html()
    
    $('form#calibrated_cameras input[name="id"]').val(id)
    
    
})

$("button#stop_calibration").on('click',function(){
    finishCalibration()
})

function acquire_image(form)
{
    $('#calibration_progress .timer').text("Acquisition in progres...");
    
    console.log($(form).attr('action'))
    camera_calibr_lock=true;
    $.ajax({
            url     : $(form).attr('action'),
            type    : $(form).attr('method'),
            //dataType: 'json',
            data    : $(form).serialize() + "&count="+camera_calibr_pic_taken,
            complete : function( data ) {
                        camera_calibr_lock=false;
            },
            error   : function( xhr, err ) {
                        console.log(err)     
            }
        });

}


function finishCalibration()
{
    clearInterval(camera_calibr_interval_handler);
    $('#calibration_progress').addClass('hidden');
}

function init_camera_calibration(form)
{
    $('#calibration_progress .timer').text("Preparing...");
    number_seconds = parseInt($(form).find('#TimelapseInterval1').val())
    number_acquisitions = parseInt($(form).find('#NumberImages').val())
    
    camera_calibr_lock = false;
      
    camera_calibr_timer= number_seconds
    
    camera_calibr_interval_handler = setInterval(function() {
        if (!camera_calibr_lock){
            $('#calibration_progress .timer').text("Acquisition in " + camera_calibr_timer + " seconds");
            
            if (camera_calibr_timer==0)
            {
                acquire_image(form)
                camera_calibr_pic_taken++;
                
                if (camera_calibr_pic_taken==number_acquisitions)
                {
                    finishCalibration()
                    window.location.reload()
                }
                
                camera_calibr_timer=number_seconds+1
                
            }
            camera_calibr_timer--;
        }
        
    }, 1000);
    
    $('#calibration_progress').removeClass('hidden');
}
