var Service;
var Characteristic;

var sys = require('sys');
    exec = require('child_process').exec;
    assign = require('object-assign');
    fileExists = require('file-exists');
    chokidar = require('chokidar');

module.exports = function(homebridge) {
  Service = homebridge.hap.Service;
  Characteristic = homebridge.hap.Characteristic;
  homebridge.registerAccessory('homebridge-script3', 'Script3', script3Accessory);
}

function puts(error, stdout, stderr) {
   console.log(stdout)
}

function script3Accessory(log, config) {
  this.log = log;

  if ('service' in config){
    this.service = config['service'];
  }
  else {
    this.service = 'Switch';
  }

  this.name = config['name'];
  this.onCommand = config['on'];
  this.offCommand = config['off'];
  this.stateCommand = config['state'] || false;
  this.onValue = config['on_value'] || "true";
  this.fileState = config['fileState'] || false;
  if (!this.fileState) {
    this.onValue = this.onValue.trim().toLowerCase();
  }
  //this.exactMatch = config['exact_match'] || true;
}

/* 
  script2Accessory.prototype.matchesString = function(match) {
  if(this.exactMatch) {
    return (match === this.onValue);
  }
  else {
    return (match.indexOf(this.onValue) > -1);
  }
}
*/

script3Accessory.prototype.setState = function(powerOn, callback) {
  var accessory = this;
  var state = powerOn ? 'on' : 'off';
  var prop = state + 'Command';
  var command = accessory[prop];

    exec(command, puts);
    accessory.log('Set ' + accessory.name + ' to ' + state);
    accessory.currentState = powerOn;
    callback(null);
}

script3Accessory.prototype.getState = function(callback) {
  var accessory = this;
  var command = accessory['stateCommand'];
  var stdout = "none";  
  
  if (this.fileState) {
    var flagFile = fileExists.sync(this.fileState);
    accessory.log('State of ' + accessory.name + ' is: ' + flagFile);
    callback(null, flagFile);
  }
  else if (this.stateCommand) {
    exec(command, function (error, stdout, stderr) {
      var cleanOut=stdout.trim().toLowerCase();
      accessory.log('State of ' + accessory.name + ' is: ' + cleanOut);
      callback(null, cleanOut == accessory.onValue);
    });
  }
  else {
      accessory.log('Must set config value for fileState or state.');
  }
}

script3Accessory.prototype.getServices = function() {
  var informationService = new Service.AccessoryInformation();
  informationService
  .setCharacteristic(Characteristic.Manufacturer, 'script3 Manufacturer')
  .setCharacteristic(Characteristic.Model, 'script3 Model')
  .setCharacteristic(Characteristic.SerialNumber, 'script3 Serial Number');

  if (this.service == 'switch'){
    var TypeService = new Service.Switch(this.name);
  }
  else if (this.service == 'heater') {
    var TypeService = new Service.Outlet(this.name);
    // var TypeService = new Service.HeaterCooler(this.name);
  }


  if (this.service == 'switch'){
    var characteristic = TypeService.getCharacteristic(Characteristic.On)
    .on('set', this.setState.bind(this));
  }
  else if (this.service == 'heater') {
    var characteristic = TypeService.getCharacteristic(Characteristic.On)
    .on('set', this.setState.bind(this));
  }

  if (this.stateCommand || this.fileState) {
    characteristic.on('get', this.getState.bind(this))
  };
  
  if (this.fileState) {
    var fileCreatedHandler = function(path, stats){
      if (!this.currentState) {
          this.log('File ' + path + ' was created');
          TypeService.setCharacteristic(Characteristic.On, true);
      }
    }.bind(this);
  
    var fileRemovedHandler = function(path, stats){
      if (this.currentState) {
          this.log('File ' + path + ' was deleted');
          TypeService.setCharacteristic(Characteristic.On, false);
	  }
    }.bind(this);
  
    var watcher = chokidar.watch(this.fileState, {alwaysStat: true});
    watcher.on('add', fileCreatedHandler);
    watcher.on('unlink', fileRemovedHandler);
  }
  return [TypeService];
}
