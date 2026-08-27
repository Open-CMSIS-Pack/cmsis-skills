#!/usr/bin/python -tt
#
############################################################
# Python script to fixup following files after an import of
# a RASC generated Renesas RA MCU uVision project by MDKv6
############################################################
# AWB : 2026-06-24 : Initial version
#       2026-07-09 : Added "hex output" to cproject.yml
############################################################

import sys
import os
import shutil
import datetime

datavalue = 0  ## initial data value

#############################################################
# Read command line arguments
# Only argument should be the directory containing the project
#############################################################

if len(sys.argv) == 1:
  # Default to current directory if no parameter given
  projdir = "."
elif len(sys.argv) == 2:
  # Should be directory containing the project
  projdir = sys.argv [1]

else:
  print ('*** Error '+sys.argv [0]+' incorrect arguments')
  sys.exit()

print ('\n=================================')
print ('= RASC project fix up for MDKv6 =')
print ('=================================')
postfix = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

realpath = os.path.abspath(projdir)
actualproj = os.path.basename(os.path.abspath(projdir))

cprojectyml_file = realpath+'/'+actualproj+'.cproject.yml'

print ("\n# Updating project's 'cproject.yml' file ...")
print ('  '+ cprojectyml_file )

# Take a backup first, just in case
shutil.copy (cprojectyml_file, cprojectyml_file+'.'+postfix)

print ('## Fixing up via file references')

with open(cprojectyml_file, 'r') as file:
  filecontent = file.read()

filecontent = filecontent.replace("@./via/rasc_armclang.via", "@$ProjectDir()$/via/rasc_armclang.via")
filecontent = filecontent.replace("./via/rasc_armasm.via", '$ProjectDir()$/via/rasc_armasm.via')
filecontent = filecontent.replace("./via/rasc_armlink.via", "$ProjectDir()$/via/rasc_armlink.via")


# Write the file out again
with open(cprojectyml_file, 'w') as file:
  file.write(filecontent)


with open(cprojectyml_file, 'a') as file:
  print ('## Adding generator')
  file.write('  generators:\n')
  file.write('    base-dir: $ProjectDir()$\n')
  file.write('    options:\n')
  file.write('    - generator: Renesas RA Smart Configurator\n')
  file.write('      path: ./\n')

  print ('## Adding Hex file output (for AC6 GDB issue)')
  # See https://open-cmsis-pack.github.io/cmsis-toolbox/Troubleshooting/#generate-hex-file
  file.write('  output:\n')
  file.write('    type:\n')
  file.write('      - elf\n')
  file.write('      - hex     # create HEX file to bypass GDB loader problem with AC6\n')
  file.write('      - map     # create MAP file (optional)\n')


linkscript_file = realpath+'/script/fsp.scat'

print ("\n# Updating project's linker scripts ...")

print ('  Main linker script : '+linkscript_file)
print ('## Fixing up paths to linker sub-scripts')

# Take a backup first, just in case
shutil.copy (linkscript_file, linkscript_file+'.'+postfix)

with open(linkscript_file, 'r') as file:
  filecontent = file.read()

filecontent = filecontent.replace("memory_regions.scat", "../memory_regions.scat")
filecontent = filecontent.replace("fsp_gen.scat", "../fsp_gen.scat")

# Write the file out again
with open(linkscript_file, 'w') as file:
  file.write(filecontent)

print ('\n# Creating post-build batch file...')

#rasc_launcher.bat "rasc_version.txt" -nosplash --launcher.suppressErrors --gensmartbundle --compiler ARMv6 --devicefamily ra "configuration.xml" "./out/RA8M1_blinky1/Target_1/RA8M1_blinky1.axf" 2> "%TEMP%/rasc_stderr.out"

postbuild_file = realpath+'/postbuild.bat'
print ('  '+postbuild_file)
string = 'call rasc_launcher.bat "rasc_version.txt" -nosplash --launcher.suppressErrors '
string = string+'--gensmartbundle --compiler ARMv6 --devicefamily ra "configuration.xml" '
string = string+'"./out/'+actualproj+'/Target_1/'+actualproj+'.axf" 2> "%TEMP%/rasc_stderr.out"'
#print (string)

with open(postbuild_file, 'w') as file:
  file.write(string+'\n')
  file.write('pause\n')

print ('\n# Creating pre-build batch file...')
prebuild_file = realpath+'/prebuild.bat'
print ('  '+prebuild_file)

#rasc_launcher.bat "rasc_version.txt" -nosplash --launcher.suppressErrors --generate --compiler ARMv6 --devicefamily ra "configuration.xml" 2> "%TEMP%\rasc_stderr.out" && echo. > "output.rasc""

string = 'call rasc_launcher.bat "rasc_version.txt" -nosplash --launcher.suppressErrors --generate --compiler ARMv6 --devicefamily ra "configuration.xml" 2> "%TEMP%\\rasc_stderr.out" && echo. > "output.rasc"'
#print (string)

with open(prebuild_file, 'w') as file:
  file.write(string+'\n')
  file.write('pause\n')

print ('\n*** Finished! ***')

sys.exit()
