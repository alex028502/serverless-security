const readFile = function(path) {
    return require('util').promisify(require('fs').readFile)(path, 'utf8');
};
const assert = require('assert');

const openpgp = require('openpgp');

assert(openpgp);

(async function(senderPublicKeyFile, recipientPrivateKeyFile) {
    // console.log('START HERE REALLY');
    // console.log(senderPublicKeyFile, recipientPrivateKeyFile, "yeah")
    const senderPublicKeyArmored = await readFile(senderPublicKeyFile);
    const recipientPrivateKeyArmored = await readFile(recipientPrivateKeyFile);
    // console.log('HERE', senderPublicKeyArmored);

    const senderPublicKey = await openpgp.readKey({
        armoredKey: senderPublicKeyArmored,
    });
    const recipientPrivateKey = await openpgp.readKey({
        armoredKey: recipientPrivateKeyArmored,
    });
    // await recipientPrivateKey.decrypt('');

    const armoredMessage = await readFile(0);
    const message = await openpgp.readMessage({
        armoredMessage: armoredMessage,
    });
    const result = await openpgp.decrypt({
        message,
        publicKeys: senderPublicKey,
        privateKeys: recipientPrivateKey,
    });
    assert(result.signatures[0].valid);
    //  console.log('GOT THIS');
    console.log(result.data);
}).apply(null, process.argv.slice(2)).catch(function(e) {
    console.error(e);
    process.exit(2);
});
