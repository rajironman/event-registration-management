// var outputImgFile = null
// var inputImgBlob = null

//// start of the block of codes for loadImage //////
/////////////////////////////////////////////////////
{
    let isCorrectlyOrientated , orientationCropBug

    // black+white 3x2 JPEG, with the following meta information set:
    // - EXIF Orientation: 6 (Rotated 90° CCW)
    // Image data layout (B=black, F=white):
    // BFF
    // BBB

    const testImageURL =
    'data:image/jpeg;base64,/9j/4QAiRXhpZgAATU0AKgAAAAgAAQESAAMAAAABAAYAAAA' +
    'AAAD/2wCEAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA' +
    'QEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE' +
    'BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAf/AABEIAAIAAwMBEQACEQEDEQH/x' +
    'ABRAAEAAAAAAAAAAAAAAAAAAAAKEAEBAQADAQEAAAAAAAAAAAAGBQQDCAkCBwEBAAAAAAA' +
    'AAAAAAAAAAAAAABEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AG8T9NfSMEVMhQ' +
    'voP3fFiRZ+MTHDifa/95OFSZU5OzRzxkyejv8ciEfhSceSXGjS8eSdLnZc2HDm4M3BxcXw' +
    'H/9k='
    const timg = document.createElement('img')
    timg.onload = function () {
        isCorrectlyOrientated = timg.width === 2 && timg.height === 3
        orientationCropBug
        if (isCorrectlyOrientated) {
            const canvas = document.createElement("canvas");
            canvasWidth = canvasWidth = 1;
            const ctx = canvas.getContext('2d')
            ctx.drawImage(timg, 1, 1, 1, 1, 0, 0, 1, 1)
            orientationCropBug =
            ctx.getImageData(0, 0, 1, 1).data.toString() !== '255,255,255,255'
        }
    }
    timg.src = testImageURL

    const transformCodes = [{'a':0,'h':0,'v':0},{'a':0,'h':0,'v':0},{'a':0,'h':1,'v':0},{'a':180,'h':0,'v':0},{'a':0,'h':0,'v':1},{'a':90,'h':0,'v':1},{'a':90,'h':0,'v':0},{'a':90,'h':1,'v':0},{'a':270,'h':0,'v':0}]
    const reverseTransformCodes = [{a:0,h:0,v:0},{a:0,h:0,v:0},{a:0,h:1,v:0},{a:180,h:0,v:0},{a:0,h:0,v:1},{a:270,h:1,v:0},{a:270,h:0,v:0},{a:270,h:0,v:1},{a:90,h:0,v:0}]

    function loadImage(inputImg,callback,ob){
        const maxWidth = ob.maxWidth
        const maxHeight = ob.maxHeight
        var exifOrientation = 1
        EXIF.getData(inputImg,function(){
            exifOrientation = parseInt(EXIF.getTag(this,'Orientation'))
        })

        const image = new Image()
        image.onload = function(){
            const index = exifOrientation
        
            const img = this
            if(URL.createObjectURL)
            URL.revokeObjectURL(this.src)
            let canvas = document.createElement('canvas')
            let ctx = canvas.getContext('2d')
            
            var imgWidth = img.naturalWidth || img.width
            var imgHeight = img.naturalHeight || img.height
            const imgRatio = imgWidth/imgHeight
            if(!(imgHeight < maxHeight && imgWidth < maxHeight))
            if((imgRatio >= maxWidth/maxHeight))
            {
                imgWidth = maxWidth
                imgHeight = maxWidth / imgRatio
            }
            else{
                imgWidth = maxHeight * imgRatio
                imgHeight = maxHeight
            }
            let canvasWidth = imgWidth
            let canvasHeight = imgHeight
            canvas.width = canvasWidth
            canvas.height = canvasHeight



            // console.log('  isCorrectlyOrientated : ',isCorrectlyOrientated,'  orientationCropBug : ',orientationCropBug)
            if(isCorrectlyOrientated && orientationCropBug && exifOrientation){
                var t
                t = reverseTransformCodes[index]
                if(t.a == 90 || t.a == 270){
                    canvasWidth = imgHeight
                    canvasHeight = imgWidth
                }
                canvas.width = canvasWidth
                canvas.height = canvasHeight            
                if(t.a!=0)
                ctx.rotate(t.a*(Math.PI/180))
                if(t.a == 90)
                ctx.translate(0,-imgHeight)
                if(t.a == 270)
                ctx.translate(-imgWidth, 0)
                if(t.a == 180)
                ctx.translate(-canvasWidth,-canvasHeight)
                if(t.h){
                    ctx.translate(imgWidth,0)
                    ctx.scale(-1,1)
                }
                if(t.v)
                {
                    ctx.translate(0,imgHeight)
                    ctx.scale(1,-1)
                }
                // ctx.beginPath()
                // ctx.moveTo(50,50)
                // ctx.lineTo(50,100)
                // ctx.stroke()
    
            }

            if(( !isCorrectlyOrientated || orientationCropBug ) && exifOrientation){
                var t = transformCodes[index]
                if(t.a == 90 || t.a == 270){
                    canvasWidth = imgHeight
                    canvasHeight = imgWidth
                }
                canvas.width = canvasWidth
                canvas.height = canvasHeight            
                if(t.a!=0)
                ctx.rotate(t.a*(Math.PI/180))
                if(t.a == 90)
                ctx.translate(0,-imgHeight)
                if(t.a == 270)
                ctx.translate(-imgWidth, 0)
                if(t.a == 180)
                ctx.translate(-canvasWidth,-canvasHeight)
                if(t.h){
                    ctx.translate(imgWidth,0)
                    ctx.scale(-1,1)
                }
                if(t.v)
                {
                    ctx.translate(0,imgHeight)
                    ctx.scale(1,-1)
                }    
            }
            ctx.drawImage(img,0,0,imgWidth,imgHeight)
            callback(canvas)
        }
        if(url = URL.createObjectURL(inputImg))
        image.src = url
        else{
            var fr = new FileReader()
            fr.onload = function(e){
                image.src = e.target.result
            }
            if(inputImg)
            fr.readAsDataURL(inputImg)
        }
    }
}


if(!HTMLCanvasElement.prototype.toBlob){
    Object.defineProperty(HTMLCanvasElement.prototype,'toBlob',{
        value:function(callback,type,quality){
            var binStr = atob(this.toDataURL(type,quality).split(',')[1]),
            len = binStr.length,
            arr = new Uint8Array(len);
            for(var i=0;i<len;i++){
                arr[i] = binStr.charCodeAt(i);
            }
            callback(new Blob([arr],{type:type || 'image/jpg'}))
        }
    });
}


function getMiddlePortionOfImage(imgFile,callback,outputImgRatio=1.6){
    var mh = 1200 , mw = 1200
    var minOutputImageHeight = 100
    var maxOutputImageHeight = 400
    var outputImgRatio = outputImgRatio || 1.6
    var outputImageType = "image/jpeg"
    var outputImageName = "image.jpeg"

    var canvas = document.createElement('canvas')
    var ctx = canvas.getContext('2d')
    loadImage(
        imgFile,function (img){
            iw = img.naturalWidth || img.width
            ih = img.naturalHeight || img.height

            if(ih < minOutputImageHeight || iw < minOutputImageHeight*1.6)
            return alert(".. புகைப்படம் குறைந்தபட்சம் "+minOutputImageHeight*1.6+"x"+minOutputImageHeight+" அளவில் இருக்க வேண்டும் ")


            if(iw/ih > outputImgRatio){
                h = ih
                w = ih*outputImgRatio
                x = iw/2 - w/2
                y = 0
            }
            else if(iw/ih < outputImgRatio){
                h = iw/outputImgRatio
                w = iw
                x = 0
                y = ih/2 - h/2
            }
            else{
                h = ih
                w = iw
                x = 0
                y = 0
            }
            
            canvas.height = Math.min(h,maxOutputImageHeight)
            canvas.width = canvas.height * outputImgRatio
            ctx.drawImage(img,x,y,w,h,0,0,canvas.width,canvas.height)


            canvas.toBlob(function(blob){
                var outputImgFile = new File([blob],outputImageName,{type:outputImageType})
                callback(outputImgFile)
            },outputImageType,0.5)
        },{orientation:true,maxHeight:mh,maxWidth:mw}
    )
}




