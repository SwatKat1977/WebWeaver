# Assertions

<table>
  <tr>
    <th>Operator</th>
    <th>Meaning</th>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>Core Comparisons</strong></td>
  </tr>
  <tr>
    <td>equals</td>
    <td><code>left == right</code></td>
  </tr>
  <tr>
    <td>not_equals</td>
    <td><code>left != right</code></td>
  </tr>
  <tr>
    <td>greater_than</td>
    <td><code>left > right</code></td>
  </tr>

  <tr>
    <td>less_than</td>
    <td><code>left < right</code></td>
  </tr>
  <tr>
    <td>contains</td>
    <td><code>right in left</code></td>
  </tr>
  <tr>
    <td>in</td>
    <td><code>left in right</code></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>String Helpers</strong></td>
  </tr>
  <tr>
    <td>starts_with</td>
    <td><code>left.startswith(right)</code></td>
  </tr>
  <tr>
    <td>ends_with</td>
    <td><code>left.endswith(right)</code></td>
  </tr>
  <tr>
    <td>matches_regex</td>
    <td><code>re.match(right, left)</code></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>Boolean</strong></td>
  </tr>
  <tr>
    <td>is_true</td>
    <td><code>bool(left) is True</code></td>
  </tr>
  <tr>
    <td>is_false</td>
    <td><code>bool(left) is False</code></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><strong>Existence</strong></td>
  </tr>
  <tr>
    <td>is_none</td>
    <td><code>left is None</code></td>
  </tr>
  <tr>
    <td>is_not_none</td>
    <td><code>left is not None</code></td>
  </tr>
</table>
