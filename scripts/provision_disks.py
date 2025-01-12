#!/usr/bin/python3
#
# scripts/provision_disks.py
# Provisions persistent disks based on prebuilt disk image for this version

import asyncio
import subprocess

rev = None
img_name = None
gcs_path = None
labels = None
project_marine_cycle = "marine-cycle-160323"
project_replit_platform_prod = "replit-platform-prod"
project_replit_platform_staging = "replit-platform-staging"
nix_flags = ['--extra-experimental-features', 'nix-command flakes discard-references']

async def main():
  global rev, img_name, gcs_path, labels
  rev = eval_rev()
  img_name = "nixmodules-%s" % rev
  gcs_path = "gs://nixmodules/%s.tar.gz" % img_name
  labels="sha=%s,service=nixmodules,component=nixmodules,cost-center=platform_packager,environment=production" % rev

  await asyncio.gather(
    create_image(project_marine_cycle, "us"),
    create_image(project_marine_cycle, "asia"),

    create_image(project_replit_platform_prod, "us"),
    create_image(project_replit_platform_prod, "asia"),

    create_image(project_replit_platform_staging, "us"),
  )
  await asyncio.gather(
    create_disk(project_marine_cycle, "asia", "asia-south1-a"),
    create_disk(project_marine_cycle, "asia", "asia-south1-b"),

    create_disk(project_marine_cycle, "us", "us-west1-a"),
    create_disk(project_marine_cycle, "us", "us-west1-b"),
    create_disk(project_marine_cycle, "us", "us-west1-c"),

    create_disk(project_marine_cycle, "us", "us-central1-a"),
    create_disk(project_marine_cycle, "us", "us-central1-c"),
    create_disk(project_marine_cycle, "us", "us-central1-f"),

    create_disk(project_marine_cycle, "us", "us-east1-b"),
    create_disk(project_marine_cycle, "us", "us-east1-c"),
    create_disk(project_marine_cycle, "us", "us-east1-d"),

    create_disk(project_replit_platform_prod, "us", "us-west1-a"),
    create_disk(project_replit_platform_prod, "us", "us-west1-b"),
    create_disk(project_replit_platform_prod, "us", "us-west1-c"),

    create_disk(project_replit_platform_prod, "us", "us-central1-a"),
    create_disk(project_replit_platform_prod, "us", "us-central1-c"),
    create_disk(project_replit_platform_prod, "us", "us-central1-f"),

    create_disk(project_replit_platform_prod, "us", "us-east1-b"),
    create_disk(project_replit_platform_prod, "us", "us-east1-c"),
    create_disk(project_replit_platform_prod, "us", "us-east1-d"),

    create_disk(project_replit_platform_prod, "asia", "asia-south1-a"),
    create_disk(project_replit_platform_prod, "asia", "asia-south1-b"),
    create_disk(project_replit_platform_prod, "asia", "asia-south1-c"),

    create_disk(project_replit_platform_staging, "us", "us-central1-a"),
    create_disk(project_replit_platform_staging, "us", "us-central1-c"),
    create_disk(project_replit_platform_staging, "us", "us-central1-f"),
  )

async def create_image(project, region):
  image_storage_location = region
  
  await async_exec([
    'gcloud', 'compute', 'images', 'create',
    '--source-uri', gcs_path,
    '--family=nixmodules',
    '--storage-location', image_storage_location,
    '--project=%s' % project,
    '--labels=%s' % labels,
    '%s-%s' % (img_name, image_storage_location)
  ])

async def create_disk(project, region, zone):
  image_storage_location = region
  await async_exec([
    'gcloud', 'compute', 'disks', 'create',
    '--type=pd-ssd',
    '--image=%s-%s' % (img_name, image_storage_location),
    '--zone=%s' % zone,
    '--project=%s' % project,
    '--labels=%s' % labels,
    '%s-%s' % (img_name, zone)
  ])

async def async_exec(cmdparts):
  cmd = ' '.join(cmdparts)
  print('Start: %s' % cmd)
  proc = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE)

  stdout, stderr = await proc.communicate()

  print('Complete: %s exit code: %d' % (cmd, proc.returncode))
  print('-->', end=None)
  stdoutStr = stdout and stdout.decode()
  stderrStr = stderr and stderr.decode()
  if stdoutStr:
    print('%s' % stdoutStr)
  if stderrStr:
    print('%s' % stderrStr)
  if proc.returncode == 0:
    return
  if stderrStr and 'already exists' in stderrStr:
    return
  raise Exception('Error running %s' % cmd)

def eval_rev():
  output = subprocess.check_output([
    'sh', '-c', 
    'nix build --refresh .#rev --print-out-paths %s \'%s\' | xargs cat' % (
      nix_flags[0], nix_flags[1]
    )
  ])
  return str(output, 'UTF-8')

if __name__ == '__main__':
  asyncio.run(main())