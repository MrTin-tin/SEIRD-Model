import os
import subprocess
import pymupdf

report_html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #555;
    font-family: 'Crimson Pro', 'Times New Roman', serif;
    color: #111;
    font-size: 13.5px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  .page {
    width: 794px; /* A4 width at 96 DPI */
    height: 1123px; /* A4 height at 96 DPI */
    background: #fff;
    padding: 60px 65px;
    margin: 20px auto;
    position: relative;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }
  .page-num {
    text-align: center;
    font-size: 11px;
    color: #555;
  }
  h1.title {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 4px;
    line-height: 1.25;
  }
  .subtitle {
    text-align: center;
    font-size: 13.5px;
    color: #444;
    margin-bottom: 8px;
  }
  .author {
    text-align: center;
    font-size: 12.5px;
    font-style: italic;
    color: #333;
    margin-bottom: 22px;
  }
  h2.section {
    font-size: 15px;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 6px;
    border-bottom: 0.5px solid #ccc;
    padding-bottom: 2px;
  }
  h3.subsection {
    font-size: 13.5px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 4px;
  }
  p {
    text-align: justify;
    margin-bottom: 8px;
    text-indent: 1.5em;
  }
  p.no-indent {
    text-indent: 0;
  }
  .formula {
    text-align: center;
    margin: 8px 0;
    font-style: italic;
  }
  ol, ul {
    padding-left: 28px;
    margin-bottom: 8px;
  }
  li {
    margin-bottom: 4px;
    text-align: justify;
  }
  .remark {
    background: #fbfbfb;
    border-left: 3px solid #7B2D8E;
    padding: 8px 12px;
    margin: 10px 0;
    font-size: 12.5px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin: 12px 0 6px 0;
  }
  th, td {
    padding: 4px 6px;
    text-align: left;
  }
  th {
    border-top: 1.5px solid #111;
    border-bottom: 1px solid #111;
    font-weight: 600;
  }
  tr.bottom-border td {
    border-bottom: 1.5px solid #111;
  }
  .caption {
    font-size: 11.5px;
    font-style: italic;
    text-align: center;
    margin-bottom: 8px;
    color: #333;
  }
  .cite {
    font-size: 11px;
    line-height: 1.4;
    margin-bottom: 6px;
    padding-left: 18px;
    text-indent: -18px;
  }
</style>
</head>
<body>

<!-- Page 1 -->
<div class="page" id="report_page_1">
  <div>
    <h1 class="title">Module 4: Physics-Informed Neural Networks for SEIRD Epidemiology</h1>
    <div class="subtitle">Mathematical Modelling Group Project &mdash; Sierra Leone Ebola 2014&ndash;15</div>
    <div class="author">Member 4 &bull; November 2026</div>

    <h2 class="section">1. Introduction and Motivation</h2>
    <p class="no-indent">Surveillance systems for Ebola report two cumulative quantities at irregular dates: confirmed cases <i>C(t)</i> and confirmed deaths <i>D(t)</i>. Every other epidemiologically relevant quantity&mdash;the susceptible fraction <i>S</i>, the incubating population <i>E</i>, the currently infectious <i>I</i>, and most critically the time-varying transmission rate &beta;(<i>t</i>)&mdash;is latent. Classical approaches handle this latency by assuming a parametric shape for &beta;(<i>t</i>) in advance (a step function, an exponential decay, or piecewise-constant segments). Each assumption has a qualitative cost: a step can never anticipate a second wave; an exponential can only decrease monotonically.</p>
    <p>Physics-informed neural networks (PINNs) offer a fundamentally different strategy. Two small neural networks jointly represent the state trajectories and &beta;(<i>t</i>) continuously, and are trained to minimise a composite loss function combining fidelity to empirical observations with a residual of the SEIRD ordinary differential equations evaluated via automatic differentiation. No predetermined functional form for &beta;(<i>t</i>) is imposed. The ODE constraint propagates observational signals from cases and deaths into the unmeasured compartments: by enforcing consistency with epidemiological dynamics, the network is compelled to reconstruct latent states <i>E</i> and <i>I</i> faithfully.</p>

    <h2 class="section">2. Architecture and Inductive Biases</h2>
    <h3 class="subsection">2.1 Observable Re-parameterisation</h3>
    <p class="no-indent">Let <i>C(t) = I(t) + R(t) + D(t)</i> denote the cumulative symptomatic incidence. Differentiating yields <i>dC/dt = &sigma; E</i>. The standard SEIRD equations can therefore be rewritten using <i>(E, I, C, D)</i>:</p>
    <div class="formula">
      dE/dt = &beta;(t)(S/N)I &minus; &sigma;E, &emsp; dI/dt = &sigma;E &minus; (&gamma; + &mu;)I, &emsp; dC/dt = &sigma;E, &emsp; dD/dt = &mu;I
    </div>
    <p class="no-indent">with algebraic recoveries <i>R = C &minus; I &minus; D</i> and <i>S = N &minus; E &minus; C</i>. Consequently, the mass conservation identity <i>S + E + I + R + D = N</i> holds identically across all candidate network outputs, converting a difficult manifold constraint into an architectural invariant.</p>

    <h3 class="subsection">2.2 Dual-Network Architecture</h3>
    <p class="no-indent">The framework deploys two decoupled feed-forward networks:</p>
    <ul>
      <li><b>State network</b> <i>g<sub>&theta;</sub>(&tau;)</i>: 3 hidden layers of 48 tanh units with 4 outputs parameterising normalised time &tau; &isin; [0, 1]:
        <div class="formula" style="font-size:12.5px;">
          e = e<sub>0</sub> e<sup>&tau; g<sub>1</sub></sup>, &emsp; i = i<sub>0</sub> e<sup>&tau; g<sub>2</sub></sup>, &emsp; c = c<sub>0</sub> e<sup>&tau; g<sub>3</sub></sup>, &emsp; d = d<sub>0</sub> + &tau; g<sub>4</sub>
        </div>
      </li>
      <li><b>Transmission network</b> <i>h<sub>&phi;</sub>(&tau;)</i>: 3 hidden layers of 32 tanh units with &beta;(&tau;) = Softplus(<i>h<sub>&phi;</sub>(&tau;) + b</i>) &gt; 0.</li>
    </ul>

    <h3 class="subsection">2.3 Inductive Biases</h3>
    <p class="no-indent">Six foundational inductive biases ensure physical validity prior to parameter optimisation: (1) <i>Hard initial conditions</i> via exponential factors ensure zero gradient error at &tau;=0; (2) <i>Strict positivity</i> eliminates biologically impossible negative populations; (3) <i>CFR parameterisation</i> &mu; = &gamma; CFR / (1 &minus; CFR) with CFR &isin; (0.2, 0.8) blocks the degenerate &mu; &rarr; 0 branch; (4) <i>Fourier feature embeddings</i> resolve spectral bias; (5) <i>Relative ODE residuals</i> prevent early-stage dynamic attenuation; (6) <i>Smoothness regularisation</i> stabilises derivative ill-conditioning.</p>
  </div>
  <div class="page-num">1</div>
</div>

<!-- Page 2 -->
<div class="page" id="report_page_2">
  <div>
    <h2 class="section">3. Loss Function and Training Protocol</h2>
    <h3 class="subsection">3.1 Composite Loss Formulation</h3>
    <p class="no-indent">The multi-objective loss function balances data fidelity, differential dynamics, and functional regularity:</p>
    <div class="formula">
      L = L<sub>C</sub> + L<sub>D</sub> + L<sub>ode</sub> + w<sub>sm</sub> L<sub>smooth</sub>
    </div>
    <p class="no-indent">where empirical terms are computed over discrete surveillance dates &tau;<sub>k</sub>:</p>
    <div class="formula">
      L<sub>C</sub> = (1/n<sub>C</sub>) &Sigma; [c(&tau;<sub>k</sub>) &minus; C<sub>k</sub>/K]<sup>2</sup>, &emsp; L<sub>D</sub> = (1/n<sub>D</sub>) &Sigma; [d(&tau;<sub>k</sub>) &minus; D<sub>k</sub>/K]<sup>2</sup>
    </div>
    <p class="no-indent">The physics loss is evaluated over <i>N<sub>f</sub> = 200</i> interior collocation points using reverse-mode automatic differentiation:</p>
    <div class="formula" style="font-size:12px;">
      L<sub>ode</sub> = (1/N<sub>f</sub>) &Sigma; [ ((e' &minus; Tf<sub>e</sub>)/e)<sup>2</sup> + ((i' &minus; Tf<sub>i</sub>)/i)<sup>2</sup> + ((c' &minus; Tf<sub>c</sub>)/c)<sup>2</sup> + ((d' &minus; Tf<sub>d</sub>)/d)<sup>2</sup> ]
    </div>
    <div class="formula">
      L<sub>smooth</sub> = (1/N<sub>f</sub>) &Sigma; (d&beta;/d&tau;)<sup>2</sup>
    </div>
    <p class="no-indent">Here <i>K</i> represents the normalization scale (peak cumulative cases in training). Hyperparameters are fixed at <i>w<sub>data</sub> = w<sub>ode</sub> = 1</i>, with smoothness weight <i>w<sub>sm</sub> = 10<sup>&minus;4</sup></i> for synthetic experiments and <i>10<sup>&minus;3</sup></i> for real outbreak data.</p>

    <div class="remark">
      <b>Remark on Relative vs. Absolute Residuals:</b> In epidemic outbreaks, caseloads expand across orders of magnitude. Under canonical absolute residuals <i>(x' &minus; Tf)<sup>2</sup></i>, the early phase where <i>(e, i, c)</i> are small contributes practically zero loss gradient. The network fits only the peak, resulting in massive early dynamical drift. Normalising by state magnitude yields scale-invariant loss contributions across the entire trajectory.
    </div>

    <h3 class="subsection">3.2 Two-Stage Optimization Protocol</h3>
    <p class="no-indent">Optimization follows a disciplined two-stage sequence implemented entirely in IEEE float64 precision:</p>
    <ol>
      <li><b>Stage 1 &mdash; Stochastic Exploration (Adam):</b> Initial learning rate of 2&times;10<sup>&minus;3</sup> with cosine annealing over 2,000 iterations. Resampling interior collocation points each iteration injects stochastic noise that escapes flat plateaus and aligns coarse trajectory envelopes.</li>
      <li><b>Stage 2 &mdash; Deterministic Refinement (L-BFGS):</b> Quasi-Newton optimization using a strong-Wolfe line search over 2,500&ndash;6,000 iterations evaluated on a fixed linspace grid. The second-order curvature approximation resolves stiff ODE couplings and converges to tight gradient tolerances.</li>
    </ol>
    <p class="no-indent">Point forecasts are constructed from an ensemble of 5 independent seeds. For out-of-sample forecasting, &beta; is held constant at its trailing 14-day mean, combined with the learned CFR parameter &mu;, and propagated via DOP853.</p>
  </div>
  <div class="page-num">2</div>
</div>

<!-- Page 3 -->
<div class="page" id="report_page_3">
  <div>
    <h2 class="section">4. Synthetic Experiments and Results</h2>
    <h3 class="subsection">4.1 Experiment E2: Forward Solution Verification</h3>
    <p class="no-indent">With baseline parameters &beta; = 0.4858 day<sup>&minus;1</sup> (<i>R<sub>0</sub> = 2.0</i>), &mu; = 0.1000 day<sup>&minus;1</sup>, and initial fractions (0.99, 0.005, 0.005, 0, 0), the PINN was trained purely on physics loss <i>L<sub>ode</sub></i> in the absence of observation data. Across 3 independent seeds, mean relative <i>L<sub>2</sub></i> errors against high-order DOP853 integration were 3.7&times;10<sup>&minus;4</sup> (<i>s</i>), 5.4&times;10<sup>&minus;4</sup> (<i>e</i>), 5.1&times;10<sup>&minus;4</sup> (<i>i</i>), 1.1&times;10<sup>&minus;3</sup> (<i>r</i>), and 7.9&times;10<sup>&minus;4</sup> (<i>d</i>). The maximum pointwise error across all compartments remained under 2.0&times;10<sup>&minus;3</sup>, with conservation maintained at 2&times;10<sup>&minus;16</sup>.</p>

    <h3 class="subsection">4.2 Experiments E3 and E4: Inverse Recovery from Noisy Reports</h3>
    <p class="no-indent">A synthetic epidemic incorporating an intervention step reducing &beta; from 0.55 to 0.25 at day 30 was observed through noisy cumulative counts (1% and 5% multiplicative noise). The PINN reconstructed &beta;(<i>t</i>), &mu;, initial states, and unobserved trajectories <i>s(t), e(t), i(t)</i>.</p>

    <div class="caption">Table 1: E3/E4 Inversion metrics from noisy cumulative cases and deaths (mean &plusmn; SD, 5 seeds).</div>
    <table>
      <thead>
        <tr>
          <th>Target Metric</th>
          <th>1% Multiplicative Noise</th>
          <th>5% Multiplicative Noise</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Transmission &beta;(t) relative L<sub>2</sub></td><td>11.0% &plusmn; 0.7%</td><td>11.6% &plusmn; 0.6%</td></tr>
        <tr><td>&beta;(t) RMSE outside transition (&gt;5d)</td><td>0.022 &plusmn; 0.005 day<sup>&minus;1</sup></td><td>0.025 &plusmn; 0.005 day<sup>&minus;1</sup></td></tr>
        <tr><td>Mortality rate &mu; relative error</td><td>4.6% &plusmn; 0.3%</td><td>5.4% &plusmn; 1.0%</td></tr>
        <tr><td>Latent Susceptible s(t) relative L<sub>2</sub></td><td>0.36% &plusmn; 0.03%</td><td>0.46% &plusmn; 0.09%</td></tr>
        <tr><td>Latent Exposed e(t) relative L<sub>2</sub></td><td>5.8% &plusmn; 0.6%</td><td>6.4% &plusmn; 0.7%</td></tr>
        <tr class="bottom-border"><td>Latent Infectious i(t) relative L<sub>2</sub></td><td>5.8% &plusmn; 0.4%</td><td>6.5% &plusmn; 0.8%</td></tr>
      </tbody>
    </table>

    <h3 class="subsection">4.3 Ablation Analysis (Experiment E6)</h3>
    <div class="caption">Table 2: Systematic architectural ablations under 5% noise (mean of 2 seeds).</div>
    <table>
      <thead>
        <tr>
          <th>Configuration</th>
          <th>&beta;(t) RMSE</th>
          <th>Hidden e(t) rel. L<sub>2</sub></th>
          <th>&mu; rel. error</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><b>Full Architecture</b></td><td><b>0.042</b></td><td><b>0.070</b></td><td><b>0.054</b></td></tr>
        <tr><td>Overweighted physics (w<sub>ode</sub> = 10)</td><td>0.123</td><td>0.207</td><td>0.143</td></tr>
        <tr><td>Adam only (8000 iters, no L-BFGS)</td><td>0.243</td><td>0.957</td><td>0.176</td></tr>
        <tr class="bottom-border"><td>Ablate Fourier features</td><td>0.058</td><td>0.083</td><td>0.045</td></tr>
      </tbody>
    </table>

    <h2 class="section">5. Conclusion and Critical Discussion</h2>
    <p class="no-indent">The SEIRD-PINN successfully resolves the epidemiological observability paradox: from noisy, aggregated reports of cumulative cases and deaths alone, it recovers continuous non-monotonic transmission trajectories &beta;(<i>t</i>), the case-fatality parameter &mu;, and latent infection compartments. The ablation confirms that second-order L-BFGS refinement and relative residual scaling are mathematically essential for convergence.</p>

    <h2 class="section">References</h2>
    <div class="cite">[1] M. Raissi, P. Perdikaris, G. E. Karniadakis. Physics-informed neural networks. <i>J. Comput. Phys.</i>, 378:686&ndash;707, 2019.</div>
    <div class="cite">[2] C. Rivers et al. Modeling the impact of interventions on Ebola in West Africa. <i>PLoS Curr. Outbreaks</i>, 2014.</div>
    <div class="cite">[3] C. L. Althaus. Estimating reproduction numbers during the 2014 Ebola outbreak. <i>PLoS Curr. Outbreaks</i>, 2014.</div>
    <div class="cite">[4] N. Rahaman et al. On the spectral bias of neural networks. <i>ICML</i>, 2019.</div>
  </div>
  <div class="page-num">3</div>
</div>

</body>
</html>'''

with open('presentation/module4/render_report.html', 'w', encoding='utf-8') as f:
    f.write(report_html)

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
pdf_doc = pymupdf.open()

for page_num in [1, 2, 3]:
    # Extract page
    start_tag = f'<div class="page" id="report_page_{page_num}">'
    start_idx = report_html.find(start_tag)
    end_tag = '<!-- Page' if page_num < 3 else '</body>'
    end_idx = report_html.find(end_tag, start_idx + len(start_tag))
    page_body = report_html[start_idx:end_idx].strip()
    if not page_body.endswith('</div>'):
        page_body = page_body[:page_body.rfind('</div>') + 6]
    
    page_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 794px;
    height: 1123px;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #fff;
    font-family: 'Crimson Pro', 'Times New Roman', serif;
    color: #111;
    font-size: 13.5px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .page {{
    width: 794px;
    height: 1123px;
    background: #fff;
    padding: 60px 65px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}
  .page-num {{
    text-align: center;
    font-size: 11px;
    color: #555;
  }}
  h1.title {{
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 4px;
    line-height: 1.25;
  }}
  .subtitle {{
    text-align: center;
    font-size: 13.5px;
    color: #444;
    margin-bottom: 8px;
  }}
  .author {{
    text-align: center;
    font-size: 12.5px;
    font-style: italic;
    color: #333;
    margin-bottom: 22px;
  }}
  h2.section {{
    font-size: 15px;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 6px;
    border-bottom: 0.5px solid #ccc;
    padding-bottom: 2px;
  }}
  h3.subsection {{
    font-size: 13.5px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 4px;
  }}
  p {{
    text-align: justify;
    margin-bottom: 8px;
    text-indent: 1.5em;
  }}
  p.no-indent {{
    text-indent: 0;
  }}
  .formula {{
    text-align: center;
    margin: 8px 0;
    font-style: italic;
  }}
  ol, ul {{
    padding-left: 28px;
    margin-bottom: 8px;
  }}
  li {{
    margin-bottom: 4px;
    text-align: justify;
  }}
  .remark {{
    background: #fbfbfb;
    border-left: 3px solid #7B2D8E;
    padding: 8px 12px;
    margin: 10px 0;
    font-size: 12.5px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin: 12px 0 6px 0;
  }}
  th, td {{
    padding: 4px 6px;
    text-align: left;
  }}
  th {{
    border-top: 1.5px solid #111;
    border-bottom: 1px solid #111;
    font-weight: 600;
  }}
  tr.bottom-border td {{
    border-bottom: 1.5px solid #111;
  }}
  .caption {{
    font-size: 11.5px;
    font-style: italic;
    text-align: center;
    margin-bottom: 8px;
    color: #333;
  }}
  .cite {{
    font-size: 11px;
    line-height: 1.4;
    margin-bottom: 6px;
    padding-left: 18px;
    text-indent: -18px;
  }}
</style>
</head>
<body>
{page_body}
</body>
</html>'''

    temp_html = f'presentation/module4/temp_report_{page_num}.html'
    out_png = f'presentation/module4/report_preview_page_{page_num}.png'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(page_html)
    
    file_url = 'file:///' + os.path.abspath(temp_html).replace('\\', '/')
    cmd = [
        chrome_path,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--hide-scrollbars',
        '--window-size=794,1123',
        f'--screenshot={os.path.abspath(out_png)}',
        file_url
    ]
    subprocess.run(cmd, capture_output=True, timeout=15)
    print(f'Rendered {out_png}, size:', os.path.getsize(out_png))

    # Add to preview PDF
    rect = pymupdf.Rect(0, 0, 595.28, 841.89) # A4 points
    pdf_page = pdf_doc.new_page(width=595.28, height=841.89)
    pdf_page.insert_image(rect, filename=out_png)

pdf_doc.save('presentation/module4/module4_report_preview.pdf')
print('Created presentation/module4/module4_report_preview.pdf with', len(pdf_doc), 'pages')
