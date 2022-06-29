# pyOCRtools
Selection of python tools, well, more workflows, for getting better results from tesseract. Original need is hook into PyAutoGUI for testing purposes.

Therefore, orientation has been made with that in mind. However, to aid flexibilty (and standalone testing), there are two routes in:
  i. via pyscreeze screenshot (which aligns with PyAutoGUI)
  ii. via opening an image file with openCV

The basic concept of the workflow is to:

  1. Acquire image (through either route noted earlier)
  
  2. Start at an entry gate, 
  3. Then walk several different paths on image manipulation simultaneously.
  4. Upon reaching the end of each path, send the images off to OCR capturing, then gauge the performance
  5. Rank each path, best to worst.
  6. Leave the exit gate of this "field"
 
  6. Downselect the best (or maybe multiples here - TBC) at the entry gate to the next field
  7. Walk further different paths on image manipulation simultaneously
  8. Upon reaching the end of each path, send the images off to OCR capturing, then gauge the performance
  9. Rank each path, best to worst.
  10. Leave the exit gate of this field

These are obviously repeatable steps.

                                                Gate n  <---------------------------------------------------------|
                                                   ||                                                             |  
                                                   \/                                                             |
                  -------------------------------------------------------------------                             |
                  ||                   ||                         ||                ||                            |
                  \/                   \/                         \/                \/                            |  
                  Path n.1            Path n.2                    Path n.3          Path n.M                      |
                  ||                   ||                         ||                ||                            |
                  -------------------------------------------------------------------                             |
                                                   ||                                                             |
                                                   \/                                                             |
                                                   Send to OCR & rank performance                                 |
                                                   ||                                                             |
                                                   \/                                                             |
                                                   Gate n+1  -----------------------------------------------------|
                                                   
Then, when all "fields" have been walked and the last gate has been exited, present the best OCR data back to the caller.
