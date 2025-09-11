# ET_Learning_Notes
## A Learning Notes Focusing on Evapotranspiration from Different Resources
<p align="center">Rui Gao<sup>1,2</sup>, Man Zhang<sup>3</sup></p>
<sup>1</sup>Department of Civil and Environmental Engineering, University of California, Merced, CA 95343, USA<br>
<sup>2</sup>Valley Institute for Sustainable Technology & Agriculture, University of California, Merced, CA 95343, USA<br>
<sup>3</sup>Center for humanities, University of California, Merced, CA 95343, USA<br>

## Reference ET
### FAO Penman-Monteith Method (FAO-56)
$$ET_o=\frac{0.408\Delta(R_n-G)+\gamma\frac{900}{T+273}u_2(e_s-e_a)}{\Delta+\gamma(1+0.34u_2)}$$

### CIMIS Method
<p align="center">
  <img src=".\Figures\CIMIS_ETo.png" alt="ETo Comparison" width="600">
  <br>
  <b>Figure 1. </b>My understanding of the CIMIS ETo calculation based on five station observations.
</p>

- For daytime ($Rn>0$)
  
$$ET_o=\frac{\Delta\times R_n}{(\Delta+\gamma)\times[694.5(1-0.000946)\times T]}[\frac{\gamma\times(e_s-e_a)}{\Delta-\gamma}\times0.125\times0.0439\times u_2] $$

- For nighttime ($Rn<=0$)
  
$$ET_o=\frac{\Delta\times R_n}{(\Delta+\gamma)\times[694.5(1-0.000946)\times T]}[\frac{\gamma\times(e_s-e_a)}{\Delta-\gamma}\times0.030\times0.576\times u_2] $$

### Hargreaves-Samani Method
$$ET_o = 0.0023 \times R_a \times (T_{mean} + 17.8) \times \sqrt{T_{max} - T_{min}}$$

## Actual ET
### TSEB models

## Acknowledgement
The authors are grateful for the funding support from the Secure Water Future (USDA NIFA # 2021-69012-35916) and Economic Development Administration Build Back Better Regional Challenge Farms-Food-Future Innovation Iniative (EDA #77907913). The authors also extend their sincere thanks to Dr. Safeeq Khan (University of California, Merced), Dr. Joshua H. Viers (University of California, Merced), and Dr. Bai Yang (Campbell Scientific, Logan) for their valuable support and guidance during hands-on experiments involving various sensors and the eddy-covariance flux tower.

## Citation
If you use this repository in your work, please cite it using the following DOI:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17102229.svg)](https://doi.org/10.5281/zenodo.17102229)

**BibTeX:**
```bibtex
@misc{gao2025learn_et,
  author       = {Rui Gao, Man Zhang},
  title        = {A Learning Notes Focusing on Evapotranspiration from Different Resources},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17102229},
  url          = {https://doi.org/10.5281/zenodo.17102229}
}
```

## Repository update information:
- **Creation date:** 2025-09-10
- **Last update:** 2025-09-10

## Contact information if issues were found:
Rui Gao<br>
Rui.Ray.Gao@gmail.com<br>
RuiGao@UCMerced.edu
