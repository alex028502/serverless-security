# pytest project

## system tests

I mainly used pytest for end to end type tests I think it is great for that.
I love the way it buffers stdin and stdout, and then shows them if there is a
test failures.

These tests are run twice.
- against the source files, while measuring test coverage
- against the practice deployment directory that we deploy to using the `local`
`ansible_connection` to to to make sure the deployments works, and that when
we add a new file and test it, it is deployed properly.

When testing the deployed application, it uses the deployed cut down venv
to run the system under test, while using the full development venv to run the
tests themselves.

The unit tests are mostly in simple files in or near the project root. They are
not run against the deployed application.

### gpiozero

Testing gpiozero was really hard. It has a "pin factory" called
[mock](https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins)
(that I ended up using), except that only works in-process, and I try to
test end to end when possible. What would have been really awesome is if
there were a mock client for the
[pigpio](https://gpiozero.readthedocs.io/en/stable/api_pins.html#module-gpiozero.pins.pigpio)
pin factory. It's meant for controlling a remote raspberry pi, but I wish
I knew how to create a fake external raspberry pi. I think it is great when
a trusted library gives you two "modes" that work the same (except when they
don't). (like how I used ansible local mode to test my ansible deployment.)[^1]
(or like using in memory sqlite for tests) It's especially great when the
library you are using has environment variables that allow you to change
modes, so that your own program doesn't really need to know the difference.
I tried looking up the protocol that `pigpio` uses, but it's over my head.

When I accepted that I needed to do something in-process to test my
programs that use `gpiozero`, I looked for an example, and couldn't find one.
I guess the main purpose is to test the `gpiozero` itself. So I had to be
creative. In [this program](../package/monitor.py) I made `SIGQUIT` drive the
input pin low and then high again, to simulate pushing the input button. Then
I check the values of the output LED pins, and print them to stdout.
I don't like having something like this that is clearly test code deployed to
the device, but I justified it to myself by saying that it could be used to
debug the program on the target device. Because it didn't want to complicate
the program with multiple signals, I only have one input pin, even though this
can be activated by both a button and the motion sensor. I could have also
used stdin to send messages to the program to drive mock pin high, but then
it would have been even harder to use for manual testing on the target device.
The [test](monitor/test_monitor.py) for this program uses the same
mechanism that I put in for manual testing.

To make use of `gpiozero`'s `mock` pin factory in
[this program](../package/sensor.py) I injected a
[generator](./mocks/sensor_timer.py) to replace the
[generator](../package/sensor_timer.py) used in production. 
In the mock generator I try all input combinations and output the output.
Then in the [test](.//test_sensor.py) I just assert that they are the
output is as expected. I also test the real generator on its own, and the
sut with the real generator just to make sure it doesn't totally fail.
This has made me finally _start_ to understand the relationship between
async/await and generators

### Code Coverage

Pretty much Every line of code in this project is covered. Everything is
instrumented in the end to end tests.  For python, you have to add
[this](coverage.pth) into your venv, and for `bash`, I used this amazing ruby
package I found: https://github.com/infertux/bashcov
For java script it's a lot easy - You just run everything inside `nyc`.
Any bash or python script that has to be used outside of the tests, is also
tested later. There is a check to make sure that all `.py` `.js` and `.sh`
files are covered.
Anything that can't be covered, the very top level that sets up coverage, or a
few other things, is directly in the two makefiles. This is conveninent because
I learned the hard way that `bashcov` doesn't work properly if there are
makefiles in the middle of the chain.  Also, with bashcov, I can't freely
`set -x`. Before I instrumented my bash, I used to make assertions that look
like this if I didn't mind a bit of extra output.

```
set -x
[[ "$x" != "" ]]
set +x
```

Now I do a check like this:

```
if [[ "$x" == "" ]]
then
    echo must set x
    exit 1
fi
```

and then I make sure that condition is covered by the tests.

Since `bashcov` only checks line coverage, and not branches, you can cheat a
bit, and decide for yourself when it is in the project's best interests to
hide a branch on a single line (maybe using `&&` and `||` to circumvent the
coverage requirement, and when you should deliberately split it over multiple
lines to allow coverage to remind you to write a test.

The conventional wisdom is that the tests themselves do not need code coverage.
Some coverage frameworks ignore anything that looks like a test file by default.
However, that is one of the places where I find it most useful. Without
measuring test coverage of tests, I might forget to delete test helpers for
example.  Also, without test coverage, a lot of people put conditions in their
tear down code that is meant to handle erros, but when the error actually
happens, tear down code that never ever runs tries to deal with it, and doesn't
usually succeed.

### The Test Pyramid

Rather than setting out to create a "test pyramid", I set out to test end to
end, and then rediscover something similar to a test pyramid each project. The
lower level tests that I end up writing always solve a specific problem, rather
than just solving the problem of "needing unit tests".
* Actually needing test support while writing a lower level component
* When the lower level component can handle countless cases that all pretty
much look the same the the higher level component. (date formatter)
* It is easier to reason about a lower level component by making it handle every
possible case even though the higher level program only uses some of them.
* Anything else where you figure out by yourself, in the context of this
specific project, that it would be too hard to cover all the possibiliities from
the highest level, but you are sure that you need the lower level component to
handle all of these cases.
* When some condition is not and can't be covered by the end to end tests but
you are sure that it has to be there.

[^1]: or like when you use in memory sqlite for tests, or even use the sqlite
mode of a database library for tests, and connect the same database library to
postgres for production. There will be cases where the two behave different,
but you will usually discover those upfront, so it is still useful for testing
the changes you make to your application.
