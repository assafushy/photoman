
var amqp = require('amqplib/callback_api');

amqp.connect('amqp://user:pass@localhost:30004', function(error0, connection) {
  if (error0) {
    throw error0;
  }
  connection.createChannel(function(error1, channel) {
    if (error1) {
      throw error1;
    }
    var queue = 'hello';

    channel.assertQueue(queue, {
      durable: false
    });
    console.log(" [*] Waiting for messages in %s.", queue);
    channel.consume(queue, function(msg) {
    console.log(" [x] Received %s", msg.content.toString());
    }, {
        noAck: true
    });
  });

    
});
