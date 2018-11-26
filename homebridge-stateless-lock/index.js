var Service, Characteristic;
var sys = require('sys');
var exec = require('child_process').exec;
//var assign = require('object-assign');
//var fileExists = require('file-exists');


module.exports = function(homebridge) {
    Service = homebridge.hap.Service;
    Characteristic = homebridge.hap.Characteristic;

    homebridge.registerAccessory("homebridge-stateless-lock", "StatelessLock", StatelessLock);
}

function StatelessLock(log, config) {
    this.log = log;
    this.name = config["name"];
    this.openCommand = config['open'];

    this.lockservice = new Service.LockMechanism(this.name);

    this.lockservice
        .getCharacteristic(Characteristic.LockCurrentState)
        .on('get', this.getState.bind(this));

    this.lockservice
        .getCharacteristic(Characteristic.LockTargetState)
        .on('set', this.setState.bind(this));

        this.newstate = Characteristic.LockCurrentState.SECURED;
        this.lockservice
            .setCharacteristic(Characteristic.LockTargetState,Characteristic.LockTargetState.SECURED);
        this.lockservice
            .setCharacteristic(Characteristic.LockCurrentState,Characteristic.LockCurrentState.SECURED);
}

StatelessLock.prototype = {
    identify: function (callback) {
        this.log("Identify requested!");
        callback();
    },

    getState: function(callback) {
        callback(null, this.newstate);
    },

    getServices: function() {
        return [this.lockservice];
    },

    setState: function(state, callback) {
        var statelessDoor = this;
        var command = this.openCommand;
        var lockState = (state == Characteristic.LockTargetState.SECURED) ? "lock" : "unlock";

        if (state == Characteristic.LockTargetState.SECURED)
        {
            callback(null);
            return;
        }
        statelessDoor.log("Set state to %s", lockState);
        callback();
        this.newstate = (state == Characteristic.LockTargetState.SECURED) ?
        Characteristic.LockCurrentState.SECURED : Characteristic.LockCurrentState.UNSECURED;
        statelessDoor
            .lockservice
            .setCharacteristic(Characteristic.LockCurrentState,this.newstate);
        exec(command);

        statelessDoor.resetDoorWithTimeout();


        // exec(command, function (error, stdout, stderr) {
        //     var cleanOut=stdout.trim().toLowerCase();
        //     statelessDoor.log('State of ' + statelessDoor.name + ' is: ' + cleanOut);
        //     statelessDoor.resetDoorWithTimeout();
        //     statelessDoor.setCharacteristic(Characteristic.LockCurrentState,Characteristic.LockCurrentState.UNSECURED);
        //     callback(null); //Characteristic.LockCurrentState, Characteristic.LockTargetState.SECURED
        //   }.bind(this));
    },

    resetDoorWithTimeout: function () {
        this.log("Resetting door to locked");
        setTimeout(function () {
            this.newstate = Characteristic.LockCurrentState.SECURED;
            this.lockservice
            .setCharacteristic(Characteristic.LockTargetState,Characteristic.LockTargetState.SECURED);
            this.lockservice
            .setCharacteristic(Characteristic.LockCurrentState,Characteristic.LockCurrentState.SECURED);
        }.bind(this), 1000);

    }
}