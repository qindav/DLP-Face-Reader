"use strict";
const express = require('express');
const app = express();
const http = require('http');
const httpServer = http.Server(app);
const io = require('socket.io')(httpServer);
const SocketIOFile = require('socket.io-file');

app.get('/', (req, res, next) => {
	return res.sendFile(__dirname + '/client/index.html');
});
app.get('/socket.io.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/socket.io-client/dist/socket.io.js');
});
app.get('/socket.io-file-client.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/socket.io-file-client/socket.io-file-client.js');
});
app.get('/buttons.js', (req, res, next) => {
	return res.sendFile(__dirname + '/client/buttons.js');
});
app.get('/setstage.js', (req, res, next) => {
	return res.sendFile(__dirname + '/client/setstage.js');
});
app.get('/three.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/build/three.js');
});
app.get('/TrackballControls.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/examples/js/controls/TrackballControls.js');
});
app.get('/OrbitControls.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/examples/js/controls/OrbitControls.js');
});
app.get('/WebGL.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/examples/js/WebGL.js');
});
app.get('/stats.min.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/examples/js/libs/stats.min.js');
});
app.get('/PCDLoader.js', (req, res, next) => {
	return res.sendFile(__dirname + '/node_modules/three/examples/js/loaders/PCDLoader.js');
});
app.get('/upload.pcd', (req, res, next) => {
	return res.sendFile(__dirname + '/data/upload.pcd');
});

io.on('connection', (socket) => {
	console.log('Socket connected.');

	var count = 0;
	var uploader = new SocketIOFile(socket, {
		uploadDir: 'data',							// simple directory
		chunkSize: 10240,							// default is 10240(1KB)
		transmissionDelay: 0,						// delay of each transmission, higher value saves more cpu resources, lower upload speed. default is 0(no delay)
		overwrite: false, 							// overwrite file if exists, default is true.
		rename: 'upload.pcd'
	});
	uploader.on('start', (fileInfo) => {
		console.log('Start uploading');
		console.log(fileInfo);
	});
	uploader.on('stream', (fileInfo) => {
		console.log(`${fileInfo.wrote} / ${fileInfo.size} byte(s)`);
	});
	uploader.on('complete', (fileInfo) => {
		console.log('Upload Complete.');
		console.log(fileInfo);
	});
	uploader.on('error', (err) => {
		console.log('Error!', err);
	});
	uploader.on('abort', (fileInfo) => {
		console.log('Aborted: ', fileInfo);
	});
});

httpServer.listen(3000, () => {
	console.log('Server listening on port 3000');
});