#rm -fR src/ build-release/
#conan source --name make --version 4.4.1 .
#conan install --name make --version 4.4.1 --profile daver .
#conan build --name make --version 4.4.1 --profile daver .
conan export-pkg --name make --version 4.4.1 --profile daver .
