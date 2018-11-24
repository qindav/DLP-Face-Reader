    if ( WEBGL.isWebGLAvailable() === false ) {
        document.body.appendChild( WEBGL.getWebGLErrorMessage() );
    }

    var camera, controls, scene, renderer, stats;
    init();
    animate();
    //drawStuff("./pcd_files/bunexample.pcd");

    function init() {
        //set up camera
        camera = new THREE.PerspectiveCamera( 20, window.innerWidth / window.innerHeight, 1, 120 );
        camera.aspect = 1.4880636604774535;
        camera.position.x = 0.7176554564070757;
        camera.position.y = 1.3330441480871489;
        camera.position.z = 1.598233929184041;
        
        camera.quaternion._x = 0.10582902121027737;
        camera.quaternion._y = 0.29564433785031075;
        camera.quaternion._z = 0.9481857261095947;
        camera.quaternion._w = 0.048357756035060484;

        camera.rotation.x = -0.6010162154869869;
        camera.rotation.y =  0.2313425650634090;
        camera.rotation.z =  3.1116621731382930;

        camera.up.x = 0.11736907037652397;
        camera.up.y = -0.3116596872897662;
        camera.up.z = 0.9429171440998325;

        //Now set up controls
        controls = new THREE.TrackballControls( camera );
        controls.rotateSpeed = 1.0;
        controls.zoomSpeed = 1.2;
        controls.panSpeed = 0.8;
        controls.noZoom = false;
        controls.noPan = false;
        controls.staticMoving = true;
        controls.dynamicDampingFactor = 0.3;
        controls.keys = [ 65, 83, 68 ];
        controls.addEventListener( 'change', render );

        // world
        scene = new THREE.Scene();
        scene.background = new THREE.Color( 0xffffff);

        // lights
        var light = new THREE.DirectionalLight( 0x002288 );
        light.position.set( 1, 1, 1 );
        scene.add( light );
        var light = new THREE.DirectionalLight( 0x002288 );
        light.position.set( -1, -1, -1 );
        scene.add( light );
        var light = new THREE.AmbientLight( 0x222222 );
        scene.add( light );

        // renderer
        renderer = new THREE.WebGLRenderer( { antialias: true } );
        renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( renderer.domElement );
        stats = new Stats();
        document.body.appendChild( stats.dom );
        window.addEventListener( 'resize', onWindowResize, false );
        render();
    }
    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize( window.innerWidth, window.innerHeight );
        controls.handleResize();
        render();
    }
    function animate() {
        requestAnimationFrame( animate );
        controls.update();
    }
    function render() {
        renderer.render( scene, camera );
        stats.update();
    }
    function cameraReset(){
        controls.reset();
    }
    function drawStuff(file){

        var url = (window.URL || window.webkitURL).createObjectURL(file);
        console.log('path', url);

        while(scene.children.length > 0){ 
            scene.remove(scene.children[0]); 
        }
            
        var loader = new THREE.PCDLoader();
        loader.load( url, function ( object ) {
            object.material.color.setHex(0x000000);
            scene.add( object );
        } );
        
        console.log("loaded");
    }
    function crapdrawStuff(fileurl){

        while(scene.children.length > 0){ 
            scene.remove(scene.children[0]); 
        }
            
        var loader = new THREE.PCDLoader();
        loader.load( fileurl, function ( object ) {
            object.material.color.setHex(0x000000);
            scene.add( object );
        } );
        
        console.log("loaded");        
    }
    