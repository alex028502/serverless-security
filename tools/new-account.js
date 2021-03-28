const fs = require('fs');
const promisify = require('util').promisify;
const writeFile = promisify(fs.writeFile);

const openpgp = require('openpgp');

(async function (directory, email, privateFilename, publicFilename) {
    await promisify(fs.mkdir)(directory);
    const keys = await openpgp.generateKey({
        userIds: [{
            name: email.split('@')[0],
            email: email,
        }],
    });
    // console.error("keys", keys);
    await writeFile(`${directory}/${privateFilename}`, keys.privateKeyArmored);
    await writeFile(`${directory}/${publicFilename}`, keys.publicKeyArmored);
    console.error(`${directory} created`);
}).apply(null, process.argv.slice(2)).catch(function(e) {
    console.error(e);
    process.exit(2);
});
