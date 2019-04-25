    if ( WEBGL.isWebGLAvailable() === false ) {
        document.body.appendChild( WEBGL.getWebGLErrorMessage() );
    }

    var parent, renderer, scene, camera, controls;
    invertToggle = true;
    init();
    animate();
    
    function init() {
        // camera
        camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 1000 );
        camera.position.set( 20, 20, 20 );

        // controls
        controls = new THREE.OrbitControls( camera );
        controls.rotateSpeed = 1.0;
        controls.zoomSpeed = 1.2;
        controls.panSpeed = 0.8;
        controls.addEventListener( 'change', render );

        // scene
        scene = new THREE.Scene();

        // renderer
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( renderer.domElement );
        stats = new Stats();
        document.body.appendChild( stats.dom ); 
        window.addEventListener( 'resize', onWindowResize, false );
        // window.addEventListener( 'wheel', onMouseWheel, false );
    }
    // function onMouseWheel( event ) {
    //     console.log("event in scroll")
    //     event.preventDefault();
    // }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize( window.innerWidth, window.innerHeight );
        render();
    } 
    function animate() {
        requestAnimationFrame( animate );
        controls.update();    
        renderer.render( scene, camera );
    }
    function render() {
        renderer.render( scene, camera );
        stats.update();
    }

    function invert(){
        if(invertToggle){
            sceneback = 0xffffff;
            scenechil = 0x000000;
            invertToggle = false;
        }
        else{
            sceneback = 0x000000;
            scenechil = 0xffffff;
            invertToggle = true;
        }
        
        scene.background = new THREE.Color( sceneback );
        for(i = 0; i < scene.children.length; i++){
            scene.children[i].material.color.setHex(scenechil);
            i++;
        }
    }
    function screenshot(){
        var w = window.open('', '');
        w.document.title = "Screenshot";
        var img = new Image();
        renderer.render(scene, camera);
        img.src = renderer.domElement.toDataURL();
        w.document.body.appendChild(img);  
    }

    //draws based on file upload
    function drawStuff(file){
        console.log(file);
        var url = (window.URL || window.webkitURL).createObjectURL(file);
        console.log('path', url);

        while(scene.children.length > 0){ 
            scene.remove(scene.children[0]); 
        }
        var loader = new THREE.PCDLoader();
        loader.load( url, function ( object ) {
            scene.add(object);
        } );
    }

    //checks file local to the server
    function distantDrawStuff(fileurl){
        console.log("in draw: " + fileurl)
        while(scene.children.length > 0){ 
            scene.remove(scene.children[0]); 
        }  
        var loader = new THREE.PCDLoader();
        loader.load( fileurl, function ( object ) {
                scene.add( object );
        } );
        alert("File loaded, drag around to refresh");
    }