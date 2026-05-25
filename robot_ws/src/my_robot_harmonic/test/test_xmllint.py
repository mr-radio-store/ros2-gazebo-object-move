# Copyright (c) 2025 YOUR NAME
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
from ament_xmllint.main import main
import pytest


@pytest.mark.linter
@pytest.mark.xmllint
def test_xmllint():
    package_dir = pathlib.Path(__file__).parent.parent
    urdf_dir = package_dir / 'urdf'
    launch_dir = package_dir / 'launch'
    
    # Check URDF/XML files
    urdf_files = []
    if urdf_dir.exists():
        urdf_files = [str(f) for f in urdf_dir.glob('*.urdf')]
        urdf_files.extend([str(f) for f in urdf_dir.glob('*.xacro')])
    
    # Check launch files (they're Python, but may contain XML)
    launch_files = []
    if launch_dir.exists():
        launch_files = [str(f) for f in launch_dir.glob('*.launch.py')]
    
    all_files = urdf_files + launch_files
    
    rc = main(argv=all_files)
    assert rc == 0, 'Found XML errors'