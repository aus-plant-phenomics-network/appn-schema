### Script for creation of GitHub Pages Visualisation

The `appn_schema_pyvizgraph.py` script is used in conjunction with a GitHub Action (see: .github/workflows/build-ttl-graph.yaml) 
to produce an interactive web-based plot of the current `appn-schma.ttl` file. 

```python
 # The script reads ./script-ghp/appn-schema.ttl.new by default
 python appn_schema_pyvizgraph.py
```

### GitHub Action to build github.io pages
The links from the nodes in the interactive graph currently point to the https://aus-plant-phenomics-network.github.io/appn-schema/ 
version of the documentation. This needs to be made up-to-date with running:
1. Ensure `.png` and `.md` files are up to date (run the `build_uml.sh` script, and push to the repo)
2. "Deploy MkDocs to Pages" GitHub Action
3. "Build TTL Schema Graph" GitHub action

The actions are available here: [https://github.com/aus-plant-phenomics-network/appn-schema/actions](https://github.com/aus-plant-phenomics-network/appn-schema/actions)
  
The built website is available here:
[https://aus-plant-phenomics-network.github.io/appn-schema/](https://aus-plant-phenomics-network.github.io/appn-schema/)

### Test the GitHub Action
From the root directory of the repository you can run:


| Task                               | Command                                   |
| ---------------------------------- | ----------------------------------------- |
| List workflows & jobs              | `act -l`                                  |
| Run a selected workflow            | `act --dryrun -j build`                   |
| Run ALL workflows                  | `act --bind`                              |
| Run workflows for a specific event | `act push`                                |
| Run ONE specific workflow file     | `act -W .github/workflows/myworkflow.yml` |
| Run a specific job                 | `act -j jobname --bind`                   |

N.B. Use the `--bind` option so that the current direcory is bound as a volume into the container.




