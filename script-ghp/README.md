# Script for creation of GitHub Pages Visualisation

The `appn_schema_pyvizgraph.py` script is used in conjunction with a GitHub Action (see: .github/workflows/build-ttl-graph.yaml) to produce an interactive web-based plot of the current `appn-schma.ttl` file. 

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




